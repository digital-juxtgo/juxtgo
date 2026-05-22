# Identity Module — Technical Documentation

**Module:** `juxtgo.apps.identity`  
**Version:** 2.3  
**Audience:** Backend Engineers, Security Team, Module Maintainers  
**Last Updated:** 2026-05-01

---

## 1. Architecture Overview

The Identity module is the **system root for all user identities, authentication, and role‑based access control (RBAC)**. It owns the custom `User` model, the `Profile` extension, and the `Role` abstraction wrapped around Django’s `Group`/`Permission` framework.

```
 ┌─────────────┐     ┌───────────────┐     ┌──────────────────┐
 │   User      │────▶│   Profile     │     │   Role           │
 │ (UUID pk)   │ 1:1 │ (avatar, etc) │     │ (name, metadata) │
 └──────┬──────┘     └───────────────┘     └────────┬─────────┘
        │                                           │
        │ M:N (through auth.User.groups)            │ 1:1 (or proxy)
        └───────────────────────────────────────────┘
                │
                ▼
       ┌──────────────────┐
       │ Django Group     │
       │ (permissions set)│
       └──────────────────┘
```

- **User** is the central authentication entity; uses email as the unique login identifier and a UUID primary key.
- **Profile** extends User with avatar, timezone, and a JSON metadata blob (stored via `models.JSONField`).
- **Role** is a semantic layer over Django’s built‑in `Group` — it provides a human‑readable name, description, and is_active flag while the underlying permissions are managed through the standard `auth_permission` M2M.
- **RBAC enforcement** happens at two levels: **coarse‑grained** (view access via `RoleRequiredMixin`) and **fine‑grained** (service/selector `has_perm` checks).

---

## 2. Model Relationships

### 2.1 User (`models/user.py`)

```python
class User(AbstractBaseUser, PermissionsMixin):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    email = models.EmailField(unique=True)
    display_name = models.CharField(max_length=150)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["display_name"]
```

- No username; authentication is email‑only.
- `PermissionsMixin` provides the `groups` and `user_permissions` M2Ms required for Django’s permission system.

### 2.2 Profile (`models/profile.py`)

```python
class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="profile")
    avatar = models.ImageField(upload_to="avatars/", blank=True)
    timezone = models.CharField(max_length=50, default="UTC")
    metadata = models.JSONField(default=dict)

    class Meta:
        constraints = [
            models.CheckConstraint(
                check=~models.Q(avatar=""),
                name="avatar_not_empty"
            )
        ]
```

- Always accessed through `user.profile` — the reverse relation is guaranteed by a post‑save signal (see below).
- `metadata` is for extensible key‑value storage (phone, job title, etc.); no fixed schema is enforced.

### 2.3 Role (`models/role.py`)

```python
class Role(models.Model):
    group = models.OneToOneField(Group, on_delete=models.CASCADE)
    display_name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return self.display_name
```

- Acts as a wrapper around Django’s `Group`. Permissions are assigned directly to the `Group` via Django admin or programmatically.
- The `is_active` flag allows disabling a role without removing the group (useful for deprecation).

### 2.4 Relationships diagram

```
User ──< groups >── Group ──< permissions >── Permission
 │                                                 │
 └── profile (OneToOne) ── Profile                 │
                                                   │
Role ── group (OneToOne) ── Group                  │
```

---

## 3. RBAC Design

### 3.1 Role–Permission Mapping

- Permissions follow the `identity.<action>_<model>` naming convention:  
  `identity.view_user`, `identity.add_user`, `identity.change_user`, `identity.deactivate_user` (custom permission), `identity.view_profile`, etc.
- Permissions are registered in `permissions/permissions.py` and created in `apps.py` `ready()`.
- A **Role** is simply a named collection of permissions stored in the associated `Group`.

Example initial roles:
| Role | Group Name | Permissions |
|------|------------|-------------|
| Administrator | `admin` | `view_user`, `add_user`, `change_user`, `deactivate_user`, `view_profile`, `change_profile` |
| Manager | `manager` | `view_user`, `view_profile` |
| User | `user` | `view_profile` (own only) |

### 3.2 Enforcement Layers

**Layer 1 — View:**  
Custom `RoleRequiredMixin` checks that `request.user.groups.filter(name__in=self.required_roles).exists()`. If false → 403.

```python
class UserListView(RoleRequiredMixin, ListView):
    required_roles = ["admin", "manager"]
    permission_required = None   # Not used
```

**Layer 2 — Service/Selector:**  
Explicit `has_perm()` calls ensure the acting user has the precise capability needed. This prevents, for example, an admin with revoked `change_user` from modifying a user via an API they can still access.

```python
def deactivate_user(*, user_id: UUID, performed_by: User) -> dict:
    if not performed_by.has_perm("identity.deactivate_user"):
        raise PermissionDenied
    ...
```

**Layer 3 — Data Scoping (Selectors):**  
Selectors apply row‑level filtering. For example, a non‑admin user fetching a user detail can only see their own record (or records within their managed scope, if hierarchical RBAC is added later).

```python
def get_user_detail(*, user_id: UUID, requestor: User) -> dict:
    if not requestor.has_perm("identity.view_user"):
        raise PermissionDenied
    qs = User.objects.filter(pk=user_id)
    if not requestor.is_staff:
        qs = qs.filter(pk=requestor.pk)   # self‑only
    return qs.values(...).first()
```

---

## 4. Service Layer Responsibilities

All write operations are in `services/account_services.py` and `services/role_services.py`. Exposed via `services/__init__.py`.

| Function                                                      | Description                                         | Transactional              | Permissions Checked             |
| ------------------------------------------------------------- | --------------------------------------------------- | -------------------------- | ------------------------------- |
| `create_user(*, email, display_name, password, performed_by)` | Creates new User + Profile                          | Yes (`transaction.atomic`) | `identity.add_user`             |
| `deactivate_user(*, user_id, performed_by)`                   | Sets `is_active=False`                              | Yes                        | `identity.deactivate_user`      |
| `update_profile(*, user_id, data, performed_by)`              | Updates profile fields (avatar, timezone, metadata) | Yes                        | `identity.change_profile`       |
| `assign_role(*, user_id, role_name, performed_by)`            | Adds user to a role’s group                         | Yes                        | `identity.assign_role` (custom) |
| `remove_role(*, user_id, role_name, performed_by)`            | Removes user from role’s group                      | Yes                        | `identity.assign_role`          |

**Error Conventions:**

- `PermissionDenied` – missing RBAC.
- `ValidationError` – input invalid (e.g., duplicate email).
- `NotFound` – user/role does not exist.
- `InvalidState` – operation invalid (e.g., deactivating already inactive user).

**Example – create_user:**

```python
@transaction.atomic
def create_user(*, email: str, display_name: str, password: str, performed_by: User) -> dict:
    if not performed_by.has_perm("identity.add_user"):
        raise PermissionDenied
    if User.objects.filter(email=email).exists():
        raise ValidationError("Email already in use.")
    user = User.objects.create(email=email, display_name=display_name)
    user.set_password(password)
    user.save()
    Profile.objects.create(user=user)
    transaction.on_commit(lambda: audit.log(actor=performed_by, action="USER_CREATED", target=user))
    transaction.on_commit(lambda: notify.send_welcome_email(user.email))
    return {"id": str(user.id), "status": "created"}
```

---

## 5. Selector Layer Usage

Read operations are in `selectors/user_selectors.py` and `selectors/role_selectors.py`.

| Function                               | Returns      | Permissions    | RBAC Scoping      |
| -------------------------------------- | ------------ | -------------- | ----------------- |
| `get_user_by_email(email, requestor)`  | `dict`       | `view_user`    | Self or admin     |
| `get_active_users(requestor)`          | `list[dict]` | `view_user`    | None (admin only) |
| `get_user_profile(user_id, requestor)` | `dict`       | `view_profile` | Self or admin     |
| `get_roles(requestor)`                 | `list[dict]` | `view_role`    | All active roles  |

**Performance:**

- `get_active_users` uses `select_related("profile")` to avoid N+1 on the profile avatar.
- Caching is not yet implemented in this version; planned to use Redis for frequently‑hit `get_roles` selectors.

**Example – get_user_profile:**

```python
def get_user_profile(*, user_id: UUID, requestor: User) -> dict:
    if not requestor.has_perm("identity.view_profile"):
        raise PermissionDenied
    qs = Profile.objects.select_related("user").filter(user_id=user_id)
    if not requestor.is_staff:
        qs = qs.filter(user=requestor)
    obj = qs.first()
    if obj is None:
        raise NotFound("Profile not found.")
    return {
        "user_id": str(obj.user_id),
        "display_name": obj.user.display_name,
        "avatar_url": obj.avatar.url if obj.avatar else None,
        "timezone": obj.timezone,
        "metadata": obj.metadata,
    }
```

---

## 6. UI Integration

All Identity pages use AdminLTE templates extended from `adminlte/base.html`. Reusable components from the UI Kit (`data_table`, `detail_card`) are included.

### 6.1 Templates

| Page            | Template                        | Context                               |
| --------------- | ------------------------------- | ------------------------------------- |
| User List       | `identity/user_list.html`       | `users` (list of dicts from selector) |
| User Detail     | `identity/user_detail.html`     | `user` (dict), `profile` (dict)       |
| Create User     | `identity/user_form.html`       | Form errors, preselected values       |
| Role Assignment | `identity/role_assignment.html` | `user`, `roles`, `current_roles`      |

### 6.2 View Example (User List)

```python
class UserListView(RoleRequiredMixin, PermissionRequiredMixin, ListView):
    required_roles = ["admin", "manager"]
    template_name = "identity/user_list.html"
    context_object_name = "users"

    def get_queryset(self):
        # Not used; overridden by get_context_data
        return User.objects.none()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["users"] = get_active_users(requestor=self.request.user)
        return context
```

- Data is already prepared as dictionaries by the selector, so the template simply iterates:  
  `{% for user in users %} ... {% endfor %}`.

---

## 7. Security Considerations

- **Password storage:** All passwords are hashed with Django’s default PBKDF2 algorithm. No plain‑text storage.
- **Session management:** Sessions are stored in Redis, not in the database, eliminating ORM‑based session fetches and reducing DB load.
- **Brute‑force protection:** Implemented through django‑axes (or custom middleware) — after 5 failed login attempts, the account is temporarily locked.
- **RBAC defensiveness:** Even if a view’s `RoleRequiredMixin` fails to catch a missing role, the Service layer duplicates the check — no mutation can be performed without explicit permission.
- **Audit trail:** Every state‑changing action (create user, deactivate, role change) produces an immutable audit log entry via `shared.audit`.
- **Sensitive data:** The `metadata` JSON field is not encrypted by default; storing sensitive data (e.g., SSN) is **forbidden** until field‑level encryption is added.

---

## 8. Known Constraints

- **No role hierarchy:** The current RBAC model is flat; roles cannot inherit permissions (e.g., “Admin” does not automatically gain “Manager” permissions, they must be assigned explicitly). This simplifies reasoning but may lead to permission duplication.
- **No multi‑tenancy:** The system assumes a single organisation; data scoping is based on `is_staff`/`requestor.pk` only. Full tenant isolation is planned for a future release.
- **No soft delete for User:** Deactivation sets `is_active=False`, but the user record is never deleted. Data retention policies must be enforced at the application layer later.
- **Profile metadata is schema‑less:** The `metadata` JSON blob can contain arbitrary keys; therefore, validation is minimal. Services must validate any expected keys manually to avoid silently ignoring malformed data.
- **Image storage:** Profile avatars are stored on the local filesystem (or a volume mount in Docker). For production, a move to S3/compatible storage is recommended but not yet implemented.

---

**Document maintainer:** Identity Module Owner  
**Review cycle:** Every major release or when RBAC model changes.
