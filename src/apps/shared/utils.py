import re
from django.utils.text import slugify


def generate_slug(name: str) -> str:
    """
    Generate a URL‑friendly slug from a name.
    Example: "My Organization" → "my-organization"
    """
    return slugify(name)


def generate_unique_slug(model_class, name: str, slug_field: str = "slug") -> str:
    """
    Generate a unique slug for a model by appending a number if it already exists.
    """
    base_slug = generate_slug(name)
    slug = base_slug
    num = 1
    while model_class.objects.filter(**{slug_field: slug}).exists():
        slug = f"{base_slug}-{num}"
        num += 1
    return slug


def truncate_string(value: str, max_length: int = 100) -> str:
    """Truncate a string to max_length and add '…' if needed."""
    if len(value) <= max_length:
        return value
    return value[: max_length - 1] + "…"
