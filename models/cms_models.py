from datetime import datetime, timezone

from extensions import db


def utcnow():
    return datetime.now(timezone.utc)


class TimestampMixin:
    created_at = db.Column(db.DateTime(timezone=True), nullable=False, default=utcnow)
    updated_at = db.Column(
        db.DateTime(timezone=True),
        nullable=False,
        default=utcnow,
        onupdate=utcnow,
    )


class PublishableMixin:
    status = db.Column(db.String(20), nullable=False, default="draft", index=True)
    display_order = db.Column(db.Integer, nullable=False, default=0, index=True)


class SoftDeleteMixin:
    """Soft delete / recycle-bin fields shared by CMS content modules."""

    is_deleted = db.Column(db.Boolean, nullable=False, default=False, index=True)
    deleted_at = db.Column(db.DateTime(timezone=True), nullable=True, index=True)
    deleted_by = db.Column(db.Integer, db.ForeignKey("admin_users.id"), nullable=True)

    def soft_meta(self):
        return {
            "is_deleted": bool(self.is_deleted),
            "deleted_at": self.deleted_at.isoformat() if self.deleted_at else None,
            "deleted_by": self.deleted_by,
        }


class AdminUser(db.Model, TimestampMixin):
    __tablename__ = "admin_users"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), nullable=False)
    email = db.Column(db.String(255), nullable=False, unique=True, index=True)
    password_hash = db.Column(db.String(255), nullable=False)
    role = db.Column(db.String(50), nullable=False, default="admin")
    is_active = db.Column(db.Boolean, nullable=False, default=True)
    last_login_at = db.Column(db.DateTime(timezone=True), nullable=True)

    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "email": self.email,
            "role": self.role,
            "is_active": self.is_active,
            "last_login_at": self.last_login_at.isoformat() if self.last_login_at else None,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }


class PasswordResetToken(db.Model):
    """One-time admin password reset tokens."""

    __tablename__ = "password_reset_tokens"

    id = db.Column(db.Integer, primary_key=True)
    admin_id = db.Column(db.Integer, db.ForeignKey("admin_users.id"), nullable=False, index=True)
    token_hash = db.Column(db.String(64), nullable=False, unique=True, index=True)
    expires_at = db.Column(db.DateTime(timezone=True), nullable=False)
    used_at = db.Column(db.DateTime(timezone=True), nullable=True)
    created_at = db.Column(db.DateTime(timezone=True), nullable=False, default=utcnow)

    admin = db.relationship("AdminUser", backref=db.backref("reset_tokens", lazy=True))


class HeroBanner(db.Model, TimestampMixin, PublishableMixin, SoftDeleteMixin):
    __tablename__ = "hero_banners"

    id = db.Column(db.Integer, primary_key=True)
    image_url = db.Column(db.String(500), nullable=False)
    title = db.Column(db.String(255), nullable=False)
    title_accent = db.Column(db.String(120), nullable=True)
    subtitle = db.Column(db.Text, nullable=True)
    description = db.Column(db.Text, nullable=True)
    primary_btn_text = db.Column(db.String(100), nullable=True)
    primary_btn_link = db.Column(db.String(500), nullable=True)
    secondary_btn_text = db.Column(db.String(100), nullable=True)
    secondary_btn_link = db.Column(db.String(500), nullable=True)

    def to_dict(self):
        return {
            "id": self.id,
            "image_url": self.image_url,
            "title": self.title,
            "title_accent": self.title_accent,
            "subtitle": self.subtitle,
            "description": self.description,
            "primary_btn_text": self.primary_btn_text,
            "primary_btn_link": self.primary_btn_link,
            "secondary_btn_text": self.secondary_btn_text,
            "secondary_btn_link": self.secondary_btn_link,
            "display_order": self.display_order,
            "status": self.status,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
            **self.soft_meta(),
        }


class HomeProject(db.Model, TimestampMixin, PublishableMixin, SoftDeleteMixin):
    __tablename__ = "home_projects"

    id = db.Column(db.Integer, primary_key=True)
    image_url = db.Column(db.String(500), nullable=False)
    title = db.Column(db.String(255), nullable=False)
    description = db.Column(db.Text, nullable=True)
    button_text = db.Column(db.String(100), nullable=True)
    button_link = db.Column(db.String(500), nullable=True)

    def to_dict(self):
        return {
            "id": self.id,
            "image_url": self.image_url,
            "title": self.title,
            "description": self.description,
            "button_text": self.button_text,
            "button_link": self.button_link,
            "display_order": self.display_order,
            "status": self.status,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
            **self.soft_meta(),
        }


class HomeEvent(db.Model, TimestampMixin, PublishableMixin, SoftDeleteMixin):
    """Upcoming events shown on the homepage teaser section."""

    __tablename__ = "home_events"

    id = db.Column(db.Integer, primary_key=True)
    image_url = db.Column(db.String(500), nullable=False)
    title = db.Column(db.String(255), nullable=False)
    description = db.Column(db.Text, nullable=True)
    venue = db.Column(db.String(255), nullable=True)
    event_date = db.Column(db.String(100), nullable=True)
    event_time = db.Column(db.String(100), nullable=True)
    registration_link = db.Column(db.String(500), nullable=True)
    button_text = db.Column(db.String(100), nullable=True)
    speaker = db.Column(db.String(255), nullable=True)

    def to_dict(self):
        return {
            "id": self.id,
            "image_url": self.image_url,
            "title": self.title,
            "description": self.description,
            "venue": self.venue,
            "event_date": self.event_date,
            "event_time": self.event_time,
            "registration_link": self.registration_link,
            "button_text": self.button_text,
            "speaker": self.speaker,
            "display_order": self.display_order,
            "status": self.status,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
            **self.soft_meta(),
        }


class Testimonial(db.Model, TimestampMixin, PublishableMixin, SoftDeleteMixin):
    __tablename__ = "testimonials"

    id = db.Column(db.Integer, primary_key=True)
    profile_image = db.Column(db.String(500), nullable=True)
    name = db.Column(db.String(120), nullable=False)
    designation = db.Column(db.String(255), nullable=True)
    organisation = db.Column(db.String(255), nullable=True)
    location = db.Column(db.String(255), nullable=True)
    message = db.Column(db.Text, nullable=False)
    rating = db.Column(db.Integer, nullable=False, default=5)

    def to_dict(self):
        return {
            "id": self.id,
            "profile_image": self.profile_image,
            "name": self.name,
            "designation": self.designation,
            "organisation": self.organisation,
            "location": self.location,
            "message": self.message,
            "rating": self.rating,
            "display_order": self.display_order,
            "status": self.status,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
            **self.soft_meta(),
        }


class FeaturedEvent(db.Model, TimestampMixin, PublishableMixin, SoftDeleteMixin):
    __tablename__ = "featured_events"

    id = db.Column(db.Integer, primary_key=True)
    banner_image = db.Column(db.String(500), nullable=False)
    title = db.Column(db.String(255), nullable=False)
    description = db.Column(db.Text, nullable=True)
    venue = db.Column(db.String(255), nullable=True)
    event_date = db.Column(db.String(100), nullable=True)
    event_time = db.Column(db.String(100), nullable=True)
    category = db.Column(db.String(100), nullable=True)
    registration_link = db.Column(db.String(500), nullable=True)

    def to_dict(self):
        return {
            "id": self.id,
            "banner_image": self.banner_image,
            "title": self.title,
            "description": self.description,
            "venue": self.venue,
            "event_date": self.event_date,
            "event_time": self.event_time,
            "category": self.category,
            "registration_link": self.registration_link,
            "display_order": self.display_order,
            "status": self.status,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
            **self.soft_meta(),
        }


class UpcomingEvent(db.Model, TimestampMixin, PublishableMixin, SoftDeleteMixin):
    """Upcoming events on the Events page grid."""

    __tablename__ = "upcoming_events"

    id = db.Column(db.Integer, primary_key=True)
    image_url = db.Column(db.String(500), nullable=False)
    title = db.Column(db.String(255), nullable=False)
    description = db.Column(db.Text, nullable=True)
    venue = db.Column(db.String(255), nullable=True)
    event_date = db.Column(db.String(100), nullable=True)
    event_time = db.Column(db.String(100), nullable=True)
    category = db.Column(db.String(100), nullable=True)
    registration_link = db.Column(db.String(500), nullable=True)

    def to_dict(self):
        return {
            "id": self.id,
            "image_url": self.image_url,
            "title": self.title,
            "description": self.description,
            "venue": self.venue,
            "event_date": self.event_date,
            "event_time": self.event_time,
            "category": self.category,
            "registration_link": self.registration_link,
            "display_order": self.display_order,
            "status": self.status,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
            **self.soft_meta(),
        }


class GalleryItem(db.Model, TimestampMixin, PublishableMixin, SoftDeleteMixin):
    __tablename__ = "gallery_items"

    id = db.Column(db.Integer, primary_key=True)
    image_url = db.Column(db.String(500), nullable=False)
    title = db.Column(db.String(255), nullable=False)
    description = db.Column(db.Text, nullable=True)
    category = db.Column(db.String(100), nullable=True)
    year = db.Column(db.String(20), nullable=True)
    location = db.Column(db.String(255), nullable=True)
    alt_text = db.Column(db.String(255), nullable=True)

    def to_dict(self):
        return {
            "id": self.id,
            "image_url": self.image_url,
            "title": self.title,
            "description": self.description,
            "category": self.category,
            "year": self.year,
            "location": self.location,
            "alt_text": self.alt_text,
            "display_order": self.display_order,
            "status": self.status,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
            **self.soft_meta(),
        }
