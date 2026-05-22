# Module Documentation: `{{ MODULE_NAME }}`

> **Template Version:** 1.0  
> **Instructions:** Copy this file into your module directory as `README.md` and replace all `{{ ... }}` placeholders. Delete any section that is not applicable, but do not alter the section structure.

---

## Purpose

Briefly describe the business domain this module solves, its primary users, and its role within JuxtGo OS.

**Example:**  
“The Identity module manages user lifecycle (creation, activation, deactivation), authentication, and RBAC role assignments. It is the single source of truth for all user accounts.”

---

## Models

| Model             | File                         | Key Fields                       | Constraints (DB-level)                     |
| ----------------- | ---------------------------- | -------------------------------- | ------------------------------------------ |
| `{{ ModelName }}` | `models/{{ model_name }}.py` | `field1 (type)`, `field2 (type)` | `UniqueConstraint(fields=[...], name=...)` |
| …                 | …                            | …                                | …                                          |

- Every model **MUST** reside in a single file inside the `models/` folder.
- Describe any special `clean()` logic, `save()` overrides (only data transformation), and Meta options.

---

## Services

List all public write‑side functions exposed by the module. Each service **MUST** be exported via `services/__init__.py`.

| Function                              | Purpose         | Transactional? | Permission Required         | Emits Events                 |
| ------------------------------------- | --------------- | -------------- | --------------------------- | ---------------------------- |
| `create_entity(*, ..., performed_by)` | Creates a new X | Yes            | `{{ app }}.add_{{ model }}` | `ENTITY_CREATED` audit event |
| …                                     | …               | …              | …                           | …                            |

**Service error handling:**  
Describe the custom exceptions this module raises and when they are triggered.

---

## Selectors

List all public read‑side functions. Each selector **MUST** be exported via `selectors/__init__.py`.

| Function                                   | Purpose                                    | RBAC Data Scoping      | Cache?               |
| ------------------------------------------ | ------------------------------------------ | ---------------------- | -------------------- |
| `get_entity_list(*, requestor, **filters)` | Returns filtered list of X visible to user | Scoped by company/role | In Redis (5 min TTL) |
| …                                          | …                                          | …                      | …                    |

**Query optimization notes:**  
Mention any `select_related`/`prefetch_related` used, or planned caching layers.

---

## Views

| View Class               | URL Name                 | HTTP Methods | Template / Response                   | Required Permission          |
| ------------------------ | ------------------------ | ------------ | ------------------------------------- | ---------------------------- |
| `{{ Resource }}ListView` | `<module>:<entity>-list` | GET          | `{{ module }}/{{ entity }}_list.html` | `{{ app }}.view_{{ model }}` |
| …                        | …                        | …            | …                                     | …                            |

- Each view **MUST** be imported in `views/__init__.py`.
- Views **MUST NOT** contain ORM access or business logic; they delegate to Services (POST/PUT) or Selectors (GET).

---

## Permissions

| Permission Codename            | Label            | Granularity        | Used By          |
| ------------------------------ | ---------------- | ------------------ | ---------------- |
| `{{ app }}.view_{{ model }}`   | View {{ model }} | Module/Model level | Selectors, Views |
| `{{ app }}.change_{{ model }}` | Edit {{ model }} | Module/Model level | Services, Views  |
| …                              | …                | …                  | …                |

- All permissions are created in `permissions/permissions.py` and registered via `ready()`.
- Custom permission checks (if any) are documented here.

---

## UI Pages

List all user‑facing pages (if applicable) provided by the module’s templates. Use descriptive page names, not just URL fragments.

| Page        | Template File                   | Description                                   |
| ----------- | ------------------------------- | --------------------------------------------- |
| User List   | `{{ module }}/user_list.html`   | Displays table of users with actions          |
| User Detail | `{{ module }}/user_detail.html` | Read‑only user profile, includes activity log |
| …           | …                               | …                                             |

- All templates extend `adminlte/base.html` and use shared UI Kit components.
- Data must be fully prepared by the view from Selector outputs; no ORM calls in templates.

---

## Dependencies

- **Internal (Core modules):**
  - `identity` — used for user permissions; communication via Shared.Nofify.
- **Internal (Shared modules):**
  - `shared.audit` — immutable activity logging.
  - `shared.notify` — email notifications.
- **External packages:** Django 4.2+, Django Guardian (only if explicitly stated).

---

## Data Flow

Describe typical request‑response lifecycle for the most important operation(s) using a step‑by‑step flow:

1. Client sends `POST /{{ module }}/{{ entity }}/` with payload.
2. View `{{ Resource }}CreateView` verifies `request.user.has_perm('{{ app }}.add_{{ model }}')`.
3. View calls `create_{{ entity }}(**form.cleaned_data, performed_by=request.user)`.
4. Service opens a transaction, performs validation, creates model instance.
5. On commit, an audit event is emitted and a cache key for relevant selectors is invalidated.
6. Service returns `{"id": new_id, "status": "created"}`.
7. View returns `JsonResponse(..., status=201)`.

---

## Constraints

- **Architectural:**
  - Service must not directly import another Core module’s service; cross‑module changes go through Shared interfaces.
  - Selectors are strictly read‑only; no `save()`, `delete()`, or `update()`.
- **Scalability:**
  - Caching strategy defined (if any) with invalidation hooks.
- **Security:**
  - All actions require a valid permission; `performed_by`/`requestor` argument is mandatory.
- **Testing:**
  - Unit tests must cover service error paths and selector RBAC filtering.
