"""CMS / knowledge → chatbot Pinecone sync (Flask backend).

After CMS content changes, export published rows + static knowledge JSON
and push incremental source updates to the FastAPI chatbot ingest API.

Never blocks the CMS request for more than a few ms (background thread).
"""

from __future__ import annotations

import json
import logging
import os
import threading
import time
from pathlib import Path
from typing import Any, Dict, List, Optional

import urllib.error
import urllib.request

logger = logging.getLogger(__name__)

_BACKEND_ROOT = Path(__file__).resolve().parents[1]
_KNOWLEDGE_DIR = _BACKEND_ROOT / "knowledge"

_LOCK = threading.Lock()
_PENDING = False
_LAST_REASON = ""
_DEBOUNCE_SECONDS = 1.5
_TIMER: Optional[threading.Timer] = None


def _chatbot_base_url() -> str:
    return (os.getenv("CHATBOT_URL") or "http://127.0.0.1:8000").rstrip("/")


def _ingest_token() -> str:
    return (os.getenv("CHATBOT_INGEST_TOKEN") or os.getenv("ADMIN_INGEST_TOKEN") or "").strip()


def _sync_enabled() -> bool:
    flag = (os.getenv("CHATBOT_SYNC_ENABLED") or "true").strip().lower()
    return flag in {"1", "true", "yes", "on"}


def _published_rows(model) -> List[Any]:
    query = model.query.filter(model.status == "published")
    if hasattr(model, "is_deleted"):
        query = query.filter(model.is_deleted.is_(False))
    return query.order_by(model.display_order.asc(), model.id.desc()).all()


def _line(label: str, value: Any) -> Optional[str]:
    if value is None:
        return None
    text = str(value).strip()
    if not text:
        return None
    return f"{label}: {text}"


def _export_cms_sources() -> Dict[str, str]:
    """Build source_name → plain-text documents from published CMS rows."""
    from models.cms_models import (
        FeaturedEvent,
        GalleryItem,
        HeroBanner,
        HomeEvent,
        HomeProject,
        Testimonial,
        UpcomingEvent,
    )

    sources: Dict[str, str] = {}

    # Home / about-ish marketing content
    home_parts: List[str] = ["# AMP India Foundation — Website Home Content (CMS)"]
    for item in _published_rows(HeroBanner):
        d = item.to_dict()
        block = [
            "## Hero banner",
            _line("Title", d.get("title")),
            _line("Accent", d.get("title_accent")),
            _line("Subtitle", d.get("subtitle")),
            _line("Description", d.get("description")),
        ]
        home_parts.append("\n".join(x for x in block if x))
    if len(home_parts) > 1:
        sources["cms_home"] = "\n\n".join(home_parts)

    # Projects
    project_parts: List[str] = ["# AMP India Foundation — Projects (CMS)"]
    for item in _published_rows(HomeProject):
        d = item.to_dict()
        block = [
            f"## Project: {d.get('title') or 'Untitled'}",
            _line("Description", d.get("description")),
            _line("Link", d.get("button_link")),
        ]
        project_parts.append("\n".join(x for x in block if x))
    if len(project_parts) > 1:
        sources["cms_projects"] = "\n\n".join(project_parts)

    # Events (home + featured + upcoming)
    event_parts: List[str] = ["# AMP India Foundation — Events (CMS)"]
    for label, model in (
        ("Home event", HomeEvent),
        ("Featured event", FeaturedEvent),
        ("Upcoming event", UpcomingEvent),
    ):
        for item in _published_rows(model):
            d = item.to_dict()
            block = [
                f"## {label}: {d.get('title') or 'Untitled'}",
                _line("Description", d.get("description")),
                _line("Venue", d.get("venue")),
                _line("Date", d.get("event_date")),
                _line("Time", d.get("event_time")),
                _line("Category", d.get("category")),
                _line("Speaker", d.get("speaker")),
                _line("Registration", d.get("registration_link")),
            ]
            event_parts.append("\n".join(x for x in block if x))
    if len(event_parts) > 1:
        sources["cms_events"] = "\n\n".join(event_parts)

    # Gallery
    gallery_parts: List[str] = ["# AMP India Foundation — Gallery (CMS)"]
    for item in _published_rows(GalleryItem):
        d = item.to_dict()
        block = [
            f"## Gallery item: {d.get('title') or 'Untitled'}",
            _line("Description", d.get("description")),
            _line("Category", d.get("category")),
            _line("Year", d.get("year")),
            _line("Location", d.get("location")),
            _line("Alt text", d.get("alt_text")),
        ]
        gallery_parts.append("\n".join(x for x in block if x))
    if len(gallery_parts) > 1:
        sources["cms_gallery"] = "\n\n".join(gallery_parts)

    # Testimonials
    testimonial_parts: List[str] = ["# AMP India Foundation — Testimonials (CMS)"]
    for item in _published_rows(Testimonial):
        d = item.to_dict()
        block = [
            f"## Testimonial: {d.get('name') or 'Anonymous'}",
            _line("Designation", d.get("designation")),
            _line("Organisation", d.get("organisation")),
            _line("Location", d.get("location")),
            _line("Message", d.get("message")),
            _line("Rating", d.get("rating")),
        ]
        testimonial_parts.append("\n".join(x for x in block if x))
    if len(testimonial_parts) > 1:
        sources["cms_testimonials"] = "\n\n".join(testimonial_parts)

    return sources


def _json_to_text(data: Any, source: str) -> str:
    lines: List[str] = [f"# AMP India Foundation — {source}"]

    def walk(node: Any, prefix: str = "") -> None:
        if isinstance(node, dict):
            for key, value in node.items():
                if key in {"keywords", "id", "page", "image_url", "banner_image"}:
                    continue
                if isinstance(value, (dict, list)):
                    walk(value, prefix=prefix)
                else:
                    walk(value, prefix=f"{prefix}{key}: ")
        elif isinstance(node, list):
            for item in node:
                walk(item, prefix=prefix)
        elif node is not None and str(node).strip():
            lines.append(f"{prefix}{node}".strip())

    walk(data)
    return "\n".join(lines)


# Map backend/knowledge JSON stems → Pinecone source ids (stable, non-colliding)
_KNOWLEDGE_SOURCE_MAP = {
    "about": "backend_about",
    "contact": "backend_contact",
    "faq": "backend_faq",
    "events": "backend_events",
    "projects": "backend_projects",
    "scholarships": "backend_scholarships",
    "volunteer": "backend_volunteer",
    "donation": "backend_donations",
    "navigation": "backend_navigation",
}


def _export_knowledge_json_sources() -> Dict[str, str]:
    sources: Dict[str, str] = {}
    if not _KNOWLEDGE_DIR.is_dir():
        return sources
    for path in sorted(_KNOWLEDGE_DIR.glob("*.json")):
        try:
            data = json.loads(path.read_text(encoding="utf-8"))
        except Exception as exc:
            logger.warning("knowledge_json_read_failed file=%s err=%s", path.name, type(exc).__name__)
            continue
        source = _KNOWLEDGE_SOURCE_MAP.get(path.stem, f"backend_{path.stem}")
        sources[source] = _json_to_text(data, path.stem)
    return sources


def build_sync_payload() -> Dict[str, Any]:
    """Collect all CMS + knowledge sources for incremental Pinecone upsert."""
    sources = {}
    sources.update(_export_cms_sources())
    sources.update(_export_knowledge_json_sources())
    return {
        "reason": _LAST_REASON or "cms_sync",
        "sources": [{"source": k, "text": v, "category": k} for k, v in sources.items()],
        "delete_missing_cms": True,
        "cms_source_prefix": "cms_",
    }


def _post_json(url: str, payload: Dict[str, Any], token: str, timeout: float = 120.0) -> Dict[str, Any]:
    body = json.dumps(payload).encode("utf-8")
    req = urllib.request.Request(
        url,
        data=body,
        method="POST",
        headers={
            "Content-Type": "application/json",
            "X-Admin-Token": token,
            "User-Agent": "aif-cms-sync/1.0",
        },
    )
    with urllib.request.urlopen(req, timeout=timeout) as resp:
        raw = resp.read().decode("utf-8", errors="replace")
        return json.loads(raw) if raw else {}


def run_chatbot_sync(reason: str = "manual") -> Dict[str, Any]:
    """Synchronously export + push to chatbot. Safe to call from a worker thread."""
    global _LAST_REASON
    _LAST_REASON = reason

    if not _sync_enabled():
        return {"success": False, "message": "CHATBOT_SYNC_ENABLED is false", "indexed": 0}

    token = _ingest_token()
    if not token or token in {"change-me", "change-me-to-a-long-random-secret"}:
        logger.warning("chatbot_sync_skipped reason=missing_or_placeholder_token")
        return {
            "success": False,
            "message": "CHATBOT_INGEST_TOKEN not configured",
            "indexed": 0,
        }

    payload = build_sync_payload()
    url = f"{_chatbot_base_url()}/api/admin/ingest/cms-sync"
    try:
        result = _post_json(url, payload, token)
        logger.info(
            "chatbot_sync_ok reason=%s indexed=%s sources=%s",
            reason,
            result.get("indexed"),
            result.get("sources"),
        )
        return {"success": True, **result}
    except urllib.error.HTTPError as exc:
        detail = exc.read().decode("utf-8", errors="replace")[:300]
        logger.error("chatbot_sync_http status=%s detail=%s", exc.code, detail)
        return {"success": False, "message": f"HTTP {exc.code}", "detail": detail, "indexed": 0}
    except Exception as exc:
        logger.error("chatbot_sync_failed error=%s", type(exc).__name__)
        return {"success": False, "message": str(type(exc).__name__), "indexed": 0}


def _flush_pending() -> None:
    global _PENDING, _TIMER
    with _LOCK:
        _PENDING = False
        _TIMER = None
        reason = _LAST_REASON or "cms_update"
    # Need Flask app context for DB queries
    try:
        from app import app

        with app.app_context():
            run_chatbot_sync(reason=reason)
    except Exception as exc:
        logger.error("chatbot_sync_flush_failed error=%s", type(exc).__name__)


def schedule_chatbot_sync(reason: str = "cms_update") -> None:
    """Debounced background sync — call after successful CMS DB commits."""
    global _PENDING, _TIMER, _LAST_REASON

    if not _sync_enabled():
        return

    with _LOCK:
        _LAST_REASON = reason
        _PENDING = True
        if _TIMER is not None:
            try:
                _TIMER.cancel()
            except Exception:
                pass
        _TIMER = threading.Timer(_DEBOUNCE_SECONDS, _flush_pending)
        _TIMER.daemon = True
        _TIMER.start()
    logger.info("chatbot_sync_scheduled reason=%s debounce=%.1fs", reason, _DEBOUNCE_SECONDS)
