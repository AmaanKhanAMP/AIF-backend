"""Registry of CMS content modules for trash, stats, and media cleanup.

Add future modules here (About, Blogs, Projects, etc.) so Trash and soft-delete
work automatically without rewriting controllers.
"""

from models.cms_models import (
    FeaturedEvent,
    GalleryItem,
    HeroBanner,
    HomeEvent,
    HomeProject,
    Testimonial,
    UpcomingEvent,
)

CONTENT_RESOURCES = [
    {
        "resource": "hero-banners",
        "module": "Hero Banners",
        "model": HeroBanner,
        "image_fields": ["image_url"],
        "title_attr": "title",
    },
    {
        "resource": "home-projects",
        "module": "Home Projects",
        "model": HomeProject,
        "image_fields": ["image_url"],
        "title_attr": "title",
    },
    {
        "resource": "home-events",
        "module": "Home Events",
        "model": HomeEvent,
        "image_fields": ["image_url"],
        "title_attr": "title",
    },
    {
        "resource": "testimonials",
        "module": "Testimonials",
        "model": Testimonial,
        "image_fields": ["profile_image"],
        "title_attr": "name",
    },
    {
        "resource": "featured-events",
        "module": "Featured Events",
        "model": FeaturedEvent,
        "image_fields": ["banner_image"],
        "title_attr": "title",
    },
    {
        "resource": "upcoming-events",
        "module": "Upcoming Events",
        "model": UpcomingEvent,
        "image_fields": ["image_url"],
        "title_attr": "title",
    },
    {
        "resource": "gallery-items",
        "module": "Gallery",
        "model": GalleryItem,
        "image_fields": ["image_url"],
        "title_attr": "title",
    },
]


def get_resource_meta(resource):
    for entry in CONTENT_RESOURCES:
        if entry["resource"] == resource:
            return entry
    return None


def get_model_meta(model):
    for entry in CONTENT_RESOURCES:
        if entry["model"] is model:
            return entry
    return None
