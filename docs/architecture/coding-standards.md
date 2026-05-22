# JuxtGo OS — Coding Standards

**Document Version:** 1.0  
**Audience:** All Developers  
**Enforcement:** Linters (flake8, mypy, isort), pre‑commit hooks, mandatory code review

All code in the JuxtGo OS monolith **MUST** comply with these standards. Any violation is grounds for automated merge rejection.

---

## 1. Python Standards

### 1.1 Naming

| Element             | Convention                                                  | Example                                |
| ------------------- | ----------------------------------------------------------- | -------------------------------------- |
| Classes             | PascalCase                                                  | `UserDeactivateView`, `OrderService`   |
| Functions / methods | snake_case                                                  | `deactivate_user`, `get_active_orders` |
| Variables           | snake_case                                                  | `user_id`, `company_list`              |
| Constants           | UPPER_SNAKE_CASE                                            | `MAX_RETRY_COUNT`, `ROLE_ADMIN`        |
| Module names        | lowercase letters, no underscores (except when unavoidable) | `identity`, `order_processing`         |
| Private members     | prefix with `_`                                             | `_internal_helper`, `_cache`           |

- **MUST NOT** use single‑letter variable names except in loops or trivial comprehensions (`[x for x in y]`).

### 1.2 Function Size

- **MUST NOT** exceed **40 lines** (body only, excluding docstring).
- Service functions **MUST** be ≤ 50 lines; Views ≤ 15 lines for `dispatch`/`get`/`post`.
- If a function grows larger, split it into well‑named private functions inside the same module.

### 1.3 Type Hints

- **ALL public functions** (services, selectors, helpers exported by `__init__.py`) **MUST** have complete type annotations for parameters and return value.
- Use `from __future__ import annotations` to enable deferred evaluation.
- Generic types: `dict`, `list`, `Optional`, `Union` — **MUST** be used explicitly.
- `Any` is **FORBIDDEN** except in truly dynamic contexts (e.g., third‑party library stubs). Prefer `object` or proper generics.
- Model fields **MUST** be typed using django‑stubs annotations (e.g., `models.CharField[...]`).

```python
def deactivate_user(*, user_id: int, performed_by: User) -> dict[str, str | int]:
    ...
```

---

## 2. Django Standards

### 2.1 Class‑Based Views (CBV)

- All views **MUST** be class‑based unless a function‑based view is explicitly simpler (e.g., a 5‑line redirect) and still adheres to RBAC decorator.
- CBVs **MUST** inherit from `PermissionRequiredMixin` (or a project‑specific variant) as the **first** base class.
- `permission_required` **MUST** be set explicitly on the view class.
- View methods (`get`, `post`) **MUST** delegate immediately to a Service (for writes) or a Selector (for reads) — no business logic, no ORM access.
- **FORBIDDEN**: overriding `dispatch` to bypass permission checks or to perform DB operations.

```python
class CompanyCreateView(PermissionRequiredMixin, CreateView):
    permission_required = "crm.add_company"
    ...
    def form_valid(self, form):
        result = create_company(**form.cleaned_data, performed_by=self.request.user)
        return JsonResponse(result)
```

### 2.2 Model Constraints

- Database‑level constraints **MUST** be defined using `Meta.constraints` (e.g., `UniqueConstraint`, `CheckConstraint`).
- `unique_together` is **DEPRECATED**; use `UniqueConstraint` with optional `condition`.
- `clean()` **ALLOWED** only for validation that must run on `ModelForm`. It **MUST NOT** contain side effects.
- `save()` overrides **MUST NOT** perform I/O outside the database; allowed only for data transformation (auto‑slug, normalisation).

### 2.3 Signals Usage

- Signals are **ALLOWED** **only** for:
  - Cache invalidation (inside the same module)
  - Low‑level audit hooks (e.g., writing to an append‑only log model)
- Signals **MUST NOT** be used to trigger core business logic — that belongs in Services.
- All signal handlers **MUST** be registered in the module’s `apps.py` `ready()` method.
- Cross‑module communication via signals is **FORBIDDEN** (use shared interfaces or Service orchestration).

---

## 3. Template Standards

### 3.1 No Business Logic

- Templates **MUST NOT** execute ORM queries. Pass **only** pre‑evaluated lists/dicts from the view context.
- Template tags/filters **MUST NOT** access the database directly.
- `{% if %}` conditions are limited to simple booleans, existence checks, and iteration — never complex decision‑making.

### 3.2 Reusability Rules

- **ALL** templates **MUST** extend `adminlte/base.html` (directly or via a module‑specific base that extends it).
- Repeated UI patterns **MUST** be extracted into shared includes under `templates/includes/` or the UI Kit.
- `{% include %}` is **MANDATED** for AdminLTE components (cards, tables, modals) from the shared UI Kit library.
- Custom template tags **MUST** live in a `templatetags/` package inside the module that owns them.

```django
{% extends "adminlte/base.html" %}
{% block content %}
  {% include "ui_kit/data_table.html" with rows=user_list %}
{% endblock %}
```

---

## 4. File Organisation Rules

- Directory layout **MUST** follow the [Module Structure Standard](#) exactly.
- One model per file in `models/`; one logical domain per file in `services/` and `selectors/`.
- Imports **MUST** be ordered: standard library → third‑party → Django → internal (juxtgo), each group separated by a blank line.
- **ALLOWED**: absolute imports for any import that crosses module boundaries (`from juxtgo.apps.identity.services import ...`).
- **FORBIDDEN**: relative imports that reach outside the current package (e.g., `from ...crm.services`). Inside the same package, relative imports are **ALLOWED** only for `__init__.py` re‑exports.

Enforced by `isort` with a custom config.

---

## 5. Commit Message Conventions

**Format:**

```
<type>(<scope>): <imperative description>

[optional body]
[optional footer]
```

| Type       | Usage                                     |
| ---------- | ----------------------------------------- |
| `feat`     | New feature                               |
| `fix`      | Bug fix                                   |
| `refactor` | Code restructure without behaviour change |
| `docs`     | Documentation only                        |
| `test`     | Test additions/improvements               |
| `chore`    | Build, CI, dependencies                   |
| `perf`     | Performance improvement                   |

- **Scope** **MUST** be the module name (e.g., `identity`, `crm`, `shared/audit`) or `core` for cross‑cutting changes.
- Description **MUST** be in imperative, lowercase, no period.
- For breaking changes, add `BREAKING CHANGE:` footer.

**Examples:**

```
feat(identity): add deactivate_user service
```

```
fix(crm): enforce permission check on company detail view
```

```
refactor(workflow): extract approval selectors into separate file
```

Branch names: `type/JIRA-ISSUE-short-description` (e.g., `feat/JUX-42-user-deactivation`).

---

## 6. Code Review Checklist

Before approving a merge request, verify that **every item** is true:

- [ ] Public functions have full type annotations.
- [ ] Views do **not** import models directly.
- [ ] Services wrap write operations in `transaction.atomic()`.
- [ ] Selectors return plain dicts/dataclasses, never ORM objects.
- [ ] No business logic in model `save()` or `clean()`.
- [ ] RBAC checks present in both view (coarse) and service/selector (fine).
- [ ] Templates extend `adminlte/base.html` and use shared UI components.
- [ ] Commit messages match the conventional format; branch name matches pattern.
- [ ] New module follows the exact required directory structure.
- [ ] No hard‑coded URLs; all URL references use `{% url %}` or `reverse()`.
- [ ] Imports are absolute; cross‑module imports go through `services`/`selectors` only.
- [ ] Tests cover service error paths and selector RBAC scoping.

**Consequence:** Any unchecked box blocks the merge until corrected.
