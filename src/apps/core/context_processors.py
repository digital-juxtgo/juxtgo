"""
Context processor that provides active_menu and active_item variables for the sidebar.
These variables drive which menu group is expanded and which child link is highlighted.

To add a new page or menu:
1. Add an entry to the URL_MAP dictionary.
   Key   = Django URL name (as defined in urls.py)
   Value = (active_menu, active_item) where:
            - active_menu  = the parent menu group ('users', 'roles', etc.)
            - active_item  = the specific child link (used to highlight)

2. In the sidebar template, use:
   - {% if active_menu == 'group_name' %}menu-open{% endif %} on the parent <li>
   - {% if active_item == 'item_name' %}active{% endif %} on the child <a>
"""

from django.urls import resolve, Resolver404

# Central mapping – modify this as you add more apps/urls
URL_MAP = {
    # Dashboard
    "index": ("", "dashboard"),
    "home": ("", "dashboard"),
    # User management
    "user_list": ("users", "user_list"),
    "user_create": ("users", "user_create"),
    "user_edit": ("users", "user_edit"),
    "user_delete": ("users", "user_delete"),
    "user_role_permission": ("users", "user_role_permission"),
    # Role & Access
    "role_list": ("roles", "role_list"),
    "role_create": ("roles", "role_create"),
    "role_edit": ("roles", "role_edit"),
    "role_delete": ("roles", "role_delete"),
    "assign_role": ("roles", "assign_role"),
    # Profile
    "profile": ("", "profile"),
    "password_change": (
        "",
        "profile",
    ),  # optional: can keep profile active on password page
    # Organizations
    "organization_list": {"menu": "organizations", "icon": "fas fa-building"},
    "organization_create": {"menu": "organizations", "icon": "fas fa-plus"},
    "organization_edit": {"menu": "organizations", "icon": "fas fa-edit"},
    "organization_delete": {"menu": "organizations", "icon": "fas fa-trash"},
}


def active_menu_context(request):
    """Return active_menu and active_item based on the current URL name."""
    try:
        url_name = resolve(request.path_info).url_name
    except Resolver404:
        return {"active_menu": "", "active_item": ""}

    menu, item = URL_MAP.get(url_name, ("", ""))
    return {"active_menu": menu, "active_item": item}
