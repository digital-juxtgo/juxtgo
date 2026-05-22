# Permissions Module – JuxtGo OS

## Overview

The **permissions** module handles Role‑Based Access Control (RBAC) for the entire platform.
It defines `Role`, provides the `RoleRequiredMixin` for views, and exposes role management UI.

## Responsibility

- Define roles (`admin`, `manager`, `support`, and custom ones)
- Assign Django permissions to roles (via Group)
- Enforce access control in views via `RoleRequiredMixin`
- Allow admin users to manage roles and assign them to users

## Architecture

The module strictly follows the **Service / Selector** pattern:

- **Selectors** return **dicts only** – they never expose ORM objects.
- **Services** perform all write operations inside `transaction.atomic()`.
- **Views** call selectors/services and never import model classes directly.

## Models

### `Role`

| Field          | Type            | Description                              |
| -------------- | --------------- | ---------------------------------------- |
| name           | CharField(50)   | Unique role name (e.g., "admin")         |
| display_name   | CharField(100)  | Human‑readable label (e.g., "Admin")     |
| group          | OneToOne(Group) | Django auth Group for permission storage |
| description    | TextField       | Optional description                     |
| is_system_role | BooleanField    | Protects essential roles from deletion   |

`Role` inherits from `shared.BaseModel` → UUID primary key, `created_at`, `updated_at`.

`save()` automatically creates or reuses a Django `Group` with the same name.

### Mixins

#### `RoleRequiredMixin`

- Accepts `required_role` (string or list).
- Allows superusers automatically.
- Checks `request.user.has_role(role_name)`.
- Returns 403 if the user lacks the required role.

## Selectors – `RoleSelector`

All methods return **lists of dicts** or a **single dict**.

| Method                     | Returns          | Description                      |
| -------------------------- | ---------------- | -------------------------------- |
| `list_roles()`             | `List[Dict]`     | All roles ordered by name        |
| `get_role_detail(role_id)` | `Optional[Dict]` | Single role with permissions IDs |

## Services – `RoleService`

All methods log their actions via `logging`.

| Method                                         | Description                                  |
| ---------------------------------------------- | -------------------------------------------- |
| `create_role(name, display_name, description)` | Uses `get_or_create` to avoid duplicates     |
| `update_role(role_id, data)`                   | Updates fields and syncs `group.permissions` |
| `delete_role(role_id)`                         | Deletes the role (and its group via CASCADE) |

## Views & Templates

| View                         | Template                                   | Access     |
| ---------------------------- | ------------------------------------------ | ---------- |
| `RoleAccessListView`         | `permissions/roles/role_access.html`       | admin only |
| `RoleCreateView`             | `permissions/roles/form.html`              | admin only |
| `RoleUpdateView`             | `permissions/roles/form.html`              | admin only |
| `RoleDeleteView`             | `permissions/roles/confirm_delete.html`    | admin only |
| `AssignRoleView`             | `permissions/roles/assign_role.html`       | admin only |
| `UserRolePermissionListView` | `identity/users/user_role_permission.html` | admin only |

All views use `BaseListView` / `BaseCreateView` / `BaseUpdateView` from `shared.views.base`.

## URL Namespace

    core:permissions:role_list
    core:permissions:role_create
    core:permissions:role_edit
    core:permissions:role_delete
    core:permissions:assign_role
    core:permissions:user_role_permission

## Sidebar Integration

The `context_processors.py` maps URL names to the `roles` menu group.
The sidebar uses `{% if active_menu == 'roles' %}menu-open{% endif %}` and highlights the active child.

## Management Command

`python manage.py seed_roles` creates `admin`, `manager`, and `support` roles if they don’t exist.

## Tests

Tests for models, selectors, and services are in `tests.py` (or future `tests/`).
Run with: `docker compose exec web python manage.py test apps.core.permissions`

## Dependencies

- `apps.core.identity` (for `User` and `UserSelector` when assigning roles)
- `apps.shared` (for `BaseModel`)
- Django’s built‑in `auth.Group` and `auth.Permission`

## Future Evolution

- Roles will become **organization‑scoped** when the `organizations` module is added.
- The `Role` model will gain an optional `organization` FK.
