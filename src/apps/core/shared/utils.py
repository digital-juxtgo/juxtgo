import re
from django.utils.text import slugify


def generate_slug(name: str) -> str:
    """
    Generate a URL‑friendly slug from a name.
    Example: "My Organization" → "my-organization"
    """
    return slugify(name)


def generate_unique_slug(model_class, name, slug_field="slug", instance=None):
    base_slug = slugify(name)
    slug = base_slug
    num = 1
    qs = model_class.objects.filter(**{slug_field: slug})
    if instance:
        qs = qs.exclude(pk=instance.pk)
    while qs.exists():
        slug = f"{base_slug}-{num}"
        num += 1
        qs = model_class.objects.filter(**{slug_field: slug})
        if instance:
            qs = qs.exclude(pk=instance.pk)
    return slug


def truncate_string(value: str, max_length: int = 100) -> str:
    """Truncate a string to max_length and add '…' if needed."""
    if len(value) <= max_length:
        return value
    return value[: max_length - 1] + "…"
