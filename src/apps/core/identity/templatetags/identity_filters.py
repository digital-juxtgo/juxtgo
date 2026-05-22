"""
Custom template filters for Identity & RBAC.
"""

from django import template
from django.conf import settings
from django.urls import resolve, Resolver404

register = template.Library()


@register.filter(name="has_role")
def has_role(user, role_name):
    """Check if user has a specific role (case‑insensitive)."""
    if not user or not user.is_authenticated:
        return False
    return user.has_role(role_name)


@register.filter
def avatar_url(user_or_dict):
    """Safely return avatar URL from dict (selector) or ORM object."""
    try:
        if isinstance(user_or_dict, dict):
            url = user_or_dict.get("avatar_url")
            return (
                url if url else f"{settings.STATIC_URL}adminlte/img/default-avatar.png"
            )
        profile = getattr(user_or_dict, "profile", None)
        if profile and profile.avatar:
            return profile.avatar.url
    except Exception:
        pass
    return f"{settings.STATIC_URL}adminlte/img/default-avatar.png"
