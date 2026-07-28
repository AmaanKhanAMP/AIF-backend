"""Upload file helpers — safe permanent deletion when media is unreferenced."""

from pathlib import Path
from urllib.parse import urlparse

from flask import current_app

from utils.content_registry import CONTENT_RESOURCES


def normalize_media_path(url):
    """Return a comparable path key for an uploaded media URL."""
    if not url or not isinstance(url, str):
        return None
    value = url.strip()
    if not value:
        return None
    if value.startswith("http://") or value.startswith("https://"):
        value = urlparse(value).path or ""
    if not value.startswith("/"):
        value = f"/{value}"
    # Only manage files under /uploads/
    if "/uploads/" not in value and not value.startswith("/uploads"):
        return None
    return value


def media_is_referenced(url, exclude_model=None, exclude_id=None):
    """True if any content row (including trashed) still references this URL."""
    key = normalize_media_path(url)
    if not key:
        return True  # external / unknown — do not delete

    candidates = {key, key.lstrip("/"), url.strip()}
    for entry in CONTENT_RESOURCES:
        model = entry["model"]
        for field in entry["image_fields"]:
            column = getattr(model, field, None)
            if column is None:
                continue
            query = model.query.filter(column.in_(list(candidates)))
            if exclude_model is model and exclude_id is not None:
                query = query.filter(model.id != exclude_id)
            if query.first():
                return True
    return False


def delete_upload_file(url):
    """Delete a local upload file from disk if it exists under UPLOAD_FOLDER."""
    key = normalize_media_path(url)
    if not key:
        return False
    # key like /uploads/hero-banners/uuid.jpg
    relative = key.split("/uploads/", 1)[-1] if "/uploads/" in key else key.lstrip("/")
    root = Path(current_app.config.get("UPLOAD_FOLDER", Path(current_app.root_path) / "uploads"))
    path = (root / relative).resolve()
    try:
        if not str(path).startswith(str(root.resolve())):
            return False
        if path.is_file():
            path.unlink()
            return True
    except OSError:
        return False
    return False


def cleanup_item_media(item, image_fields, exclude_self=True):
    """Remove uploaded files for an item that are no longer referenced elsewhere."""
    deleted = []
    for field in image_fields:
        url = getattr(item, field, None)
        if not url:
            continue
        referenced = media_is_referenced(
            url,
            exclude_model=item.__class__ if exclude_self else None,
            exclude_id=item.id if exclude_self else None,
        )
        if not referenced and delete_upload_file(url):
            deleted.append(url)
    return deleted
