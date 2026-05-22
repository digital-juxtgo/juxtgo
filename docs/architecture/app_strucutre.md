# JuxtGo OS — Module Structure Standard

**Document Version:** 1.0  
**Audience:** Backend Developers, Module Owners  
**Enforcement:** CI checks, code review

Every Django application (module) inside `juxtgo/apps/` **MUST** conform to this specification. No deviations without approval from the architecture team.

---

## 1. Required Directory Structure

```
juxtgo/apps/<module>/
├── __init__.py
├── apps.py                    # AppConfig, verbose_name = "<Module>"
├── urls.py                    # URL configuration with app_name
├── models/
│   ├── __init__.py            # Imports all model classes
│   └── <model_name>.py        # One file per model (singular, snake_case)
├── services/
│   ├── __init__.py            # Re‑exports all public service functions
│   └── <domain>_services.py   # Logical grouping of write operations
├── selectors/
│   ├── __init__.py            # Re‑exports all public selector functions
│   └── <entity>_selectors.py  # Query functions per aggregate/entity
├── views/
│   ├── __init__.py            # Imports and exposes all view classes/functions
│   └── <resource>_views.py    # One view file per resource or functional area
├── permissions/
│   ├── __init__.py            # Re‑exports custom permissions and decorators
│   └── permissions.py         # Permission constants, setup, checks
├── templates/
│   └── <module>/              # All templates MUST live inside module-named subfolder
│       ├── base.html          # (optional) module-level base template
│       └── ...                # page-specific templates
└── migrations/                # Managed by Django; MUST exist
    └── __init__.py
```

**Inclusion rule:** The folders `models/`, `services/`, `selectors/`, `views/`, `permissions/`, `templates/` are **mandatory** for every module, even if initially empty (with an `__init__.py`). Tests go into `tests/` at the module root (not detailed here).

---

## 2. File Naming Conventions

| Element          | Convention                                           | Examples                                   |
| ---------------- | ---------------------------------------------------- | ------------------------------------------ |
| Module directory | Lowercase, no underscores (abbreviations OK)         | `identity`, `crm`, `workflow`              |
| Model files      | Singular, snake_case                                 | `user.py`, `company.py`, `opportunity.py`  |
| Service files    | `<domain>_services.py`                               | `account_services.py`, `order_services.py` |
| Selector files   | `<entity>_selectors.py`                              | `user_selectors.py`, `order_selectors.py`  |
| View files       | `<resource>_views.py`                                | `user_views.py`, `dashboard_views.py`      |
| Permission files | `permissions.py` **exactly** (inside `permissions/`) | –                                          |
| Template files   | kebab-case or snake_case, meaningful                 | `user_detail.html`, `company_list.html`    |

**Enforcement:** Any file placed outside these naming patterns **MUST NOT** be imported by other modules and is considered private.

---

## 3. Folder Responsibilities

### models/

- **MUST** contain exactly one file per database model.
- `__init__.py` **MUST** import every model explicitly: `from .user import User`.
- Model classes **MUST NOT** contain business logic beyond data integrity constraints (see Architecture doc).
- **ALLOWED**: `class Meta`, `clean()`, overridden `save()` **only** for field transformations.
- **FORBIDDEN**: imports from `services`, `selectors`, `views`, or any external I/O.

### services/

- **MUST** expose all public write‑side functions via `__init__.py`.
- Functions **MUST** be grouped into logical files (`<domain>_services.py`).
- Every service function is **stateless** (no class instances) and follows the signature rules from the Backend Architecture document.
- **MUST NOT** access the request object or HTTP constructs.

### selectors/

- **MUST** expose all public read‑side functions via `__init__.py`.
- **MUST NOT** perform writes; they are tested to ensure no INSERT/UPDATE/DELETE.
- Query logic **MUST** remain inside the selector function, never in the caller.

### views/

- **MUST** contain all HTTP entry points (class‑based views or thin function views).
- `__init__.py` **MUST** import all view classes/functions so that `from .views import ...` works for every view.
- Views **MUST NOT** import Models directly; they **MUST** use Services/Selectors.

### permissions/

- **MUST** define the module’s permission codenames (e.g., `"identity.view_user"`) as module‑level constants.
- **MUST** provide any custom `PermissionRequiredMixin` or decorator **if** the module extends the standard RBAC checks.
- Permission postsave signals (creating `Permission` objects) may live here.

### templates/

- **MUST** reside in `<module>/templates/<module>/` to avoid name collisions.
- **MUST** adhere to the Template Rules (Section 4).

---

## 4. Template Rules

1. **Base extension:** Every HTML template **MUST** extend `adminlte/base.html` (or `shared_ui/base.html` if provided) using `{% extends "adminlte/base.html" %}`.
2. **Shared components:** Developers **MUST** use the shared UI components (cards, tables, modals, form helpers) from the `ui_kit` template tag library. Do **NOT** duplicate HTML structure.
3. **No embedded logic:** Templates **MUST NOT** contain business logic or ORM queries. All data **MUST** be provided by the view context as the output of Selectors.
4. **Static resource handling:** CSS/JS **MUST** go through Django’s static pipeline, using `{% static %}`, with files placed in the module’s `static/<module>/` directory if necessary.
5. **URLs:** All links **MUST** use `{% url '<module>:<name>' ... %}`. Hard‑coded URLs are **FORBIDDEN**.

---

## 5. URL Structure

Every module exposes a single `urls.py`:

```python
# juxtgo/apps/identity/urls.py
from django.urls import path
from .views import UserListView, UserDeactivateView

app_name = "identity"

urlpatterns = [
    path("users/", UserListView.as_view(), name="user-list"),
    path("users/<int:pk>/deactivate/", UserDeactivateView.as_view(), name="user-deactivate"),
]
```

**Rules:**

- `app_name` **MUST** match the module directory name.
- URL pattern names **MUST** follow the format `<entity>-<action>` (lowercase, hyphens).
- All module URLs **MUST** be included in the project’s main `urls.py` with a namespace identical to `app_name`:
  ```python
  path("identity/", include("juxtgo.apps.identity.urls", namespace="identity"))
  ```
- No two modules may share the same namespace.
- Views **MUST** be imported from `.views` (never a deeper path) to keep the API surface explicit.

---

## 6. Example Module Layout: Identity

```
juxtgo/apps/identity/
├── __init__.py
├── apps.py
├── urls.py
├── models/
│   ├── __init__.py             # from .user import User
│   └── user.py                 # class User(AbstractUser): ...
├── services/
│   ├── __init__.py             # from .account_services import create_user, deactivate_user
│   └── account_services.py
├── selectors/
│   ├── __init__.py             # from .user_selectors import get_user_by_email, get_active_users
│   └── user_selectors.py
├── views/
│   ├── __init__.py             # from .user_views import UserListView, UserDeactivateView
│   └── user_views.py
├── permissions/
│   ├── __init__.py             # from .permissions import IDENTITY_PERMISSIONS, register_permissions
│   └── permissions.py
├── templates/
│   └── identity/
│       ├── user_list.html
│       └── user_detail.html
└── migrations/
    └── __init__.py
```

---

## 7. Validation Checklist for New Modules

Before a new module is merged, the following **MUST** all be true:

- [ ] Directory structure exactly matches Section 1.
- [ ] `models/__init__.py` imports every model; no model file is overlooked.
- [ ] `services/__init__.py` exports every public service function; **no** service file is imported directly from outside.
- [ ] `selectors/__init__.py` exports every public selector function.
- [ ] `views/__init__.py` imports all view classes/functions used in `urls.py`.
- [ ] `permissions/__init__.py` exports any custom permission utilities.
- [ ] Templates extend `adminlte/base.html` and use shared components.
- [ ] URL namespace equals module name; all pattern names use `<entity>-<action>`.
- [ ] No hard‑coded URLs in any template or Python file.
- [ ] Static analysis confirms that views do not import `models` directly.
- [ ] Selector functions contain no write operations (verified by test suite).
- [ ] Service functions use `transaction.atomic()` where mutations occur.
- [ ] All cross‑module imports go through `services` or `selectors` (never bypassing the public API).
- [ ] Module’s `AppConfig.verbose_name` is set and matches the directory name in title case.

**Consequence of violation:** Merge request is blocked until the module is restructured or the exception is approved by the architecture lead.
