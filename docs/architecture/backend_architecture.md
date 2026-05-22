# JuxtGo OS — Strict Backend Architecture

**Document Version:** 2.1  
**Audience:** Backend Engineers, QA, Code Reviewers  
**Enforcement Level:** Mandatory (CI‑enforced)

This document defines **non‑negotiable** rules for all backend code in the JuxtGo OS monolith. Violations cause merge‑request rejection.

---

## 1. Layer Responsibilities

| Layer         | Primary Responsibility                                                                                          | ALLOWED Operations                                                                                                                                                                                                                    | FORBIDDEN Operations                                                                                                                                                                                     |
| ------------- | --------------------------------------------------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| **Models**    | Data schema definition and low‑level integrity constraints.                                                     | Define fields, Meta, `clean()`, overridden `save()` only for data transformation (e.g., auto‑slug, timezone fixes).                                                                                                                   | **MUST NOT** contain business logic, call external services, send notifications, or modify other models beyond simple denormalisation. `save()` overrides **MUST NOT** perform I/O other than DB writes. |
| **Services**  | Orchestrate write‑side business logic and enforce transactional consistency.                                    | Validate permissions, coordinate multiple model updates, `transaction.atomic()`, emit domain events (audit, notifications) **after** commit. **ALLOWED** to import and call Selectors for read‑only data needed during the operation. | **MUST NOT** return ORM objects. **MUST NOT** use `get()` or `filter()` directly on models; all queries **MUST** go through Selectors (except internal aggregation within the same module’s service).    |
| **Selectors** | Read‑side data retrieval with optimised queries and built‑in RBAC scoping.                                      | Build composable `QuerySet` chains, apply `select_related`, `prefetch_related`, tenant/role‑based filters. Return plain Python structures (dicts, dataclasses, lists).                                                                | **MUST NOT** perform any write operation (`save()`, `delete()`, `update()`, `create()`). **MUST NOT** start transactions. **MUST NOT** contain business logic beyond field filtering.                    |
| **Views**     | HTTP boundary: parse request, enforce coarse‑grained RBAC, delegate to Services/Selectors, and render response. | Access request, call a **single** Service (for mutations) or **a chain of Selectors** (for reads), build template context or JSON response.                                                                                           | **MUST NOT** import Models directly. **MUST NOT** call `save()`, `delete()`, or `create()` on any object. **MUST NOT** contain business rules.                                                           |

---

## 2. Dependency Rules

```
Allowed direction:
Views → Services / Selectors
Services → Selectors, Models
Selectors → Models
Models → nothing (except standard Django fields)
```

| Layer        | Can access                                                                                           | MUST NOT access                                                            |
| ------------ | ---------------------------------------------------------------------------------------------------- | -------------------------------------------------------------------------- |
| **View**     | Services (`juxtgo.apps.core.identity.services`), Selectors, Django forms/serializers, request object | Models, `QuerySet` methods, ORM objects                                    |
| **Service**  | Selectors, Models (same module), shared modules (Audit, Notify), `transaction.atomic()`              | Views, other Core modules’ Services directly (use events/shared interface) |
| **Selector** | Models, `QuerySet` API, Redis cache                                                                  | Views, Services, `transaction.atomic()`                                    |
| **Model**    | Fields, Django’s `Model` methods                                                                     | Services, Selectors, Views, any business‑rule logic                        |

**Cross‑module rule:**

- Core modules **MUST NOT** import from another Core module’s `services.py` or `selectors.py`.
- Cross‑cutting integration passes through **Shared modules** (e.g., `Shared.Audit`, `Shared.Notify`) or Django signals with synchronous dispatchers.

---

## 3. Forbidden Patterns (Explicit)

### 3.1 ORM in views (FORBIDDEN)

```python
# ❌ ANTI‑PATTERN
def user_detail(request, user_id):
    user = User.objects.get(id=user_id)          # ORM directly in view
    return render(request, "user_detail.html", {"user": user})
```

**Enforcement:** Static analysis rules flag any `from django.db.models import ...` inside `views.py`.

### 3.2 Business logic in models (FORBIDDEN)

```python
# ❌ ANTI‑PATTERN
class Order(models.Model):
    def submit(self):
        if self.status != "draft":
            raise ValueError
        self.status = "submitted"
        self.save()
        send_email()                              # side effect in model
```

**Correct approach:** Service handles state transition and side effects.

### 3.3 Direct `save()` in views (FORBIDDEN)

```python
# ❌ ANTI‑PATTERN
def approve_order(request, order_id):
    order = Order.objects.get(id=order_id)
    order.status = "approved"
    order.save()                                  # direct mutation from view
```

### 3.4 Selector returning ORM objects across module boundaries (FORBIDDEN)

```python
# ❌ In a CRM selector
from identity.models import User
def get_sales_rep(rep_id):
    return User.objects.get(id=rep_id)            # Exposes full ORM object
```

**Requirement:** Transform to dict/dataclass before returning.

---

## 4. Service Layer Design

### 4.1 Function structure

Every Service function **MUST**:

- Accept keyword‑only arguments (except optional `performed_by`).
- Perform an initial permission check using `performed_by.has_perm()`.
- Wrap all database mutations inside `transaction.atomic()`.
- Call **only Selectors** for any necessary reads during the transaction.
- Emit events (audit, notifications) using `transaction.on_commit()` to prevent side‑effects within a rolled‑back transaction.

```python
# juxtgo/apps/crm/services.py
from juxtgo.shared.audit.services import log_event, AuditAction

def close_opportunity(*, opportunity_id: int, performed_by: User) -> dict:
    if not performed_by.has_perm("crm.change_opportunity"):
        raise PermissionDenied

    with transaction.atomic():
        opp = Opportunity.objects.select_for_update().get(id=opportunity_id)
        if opp.status != "open":
            raise InvalidState("Opportunity is not open.")
        opp.status = "closed"
        opp.closed_by = performed_by
        opp.save(update_fields=["status", "closed_by"])

        transaction.on_commit(lambda: log_event(
            actor=performed_by,
            action=AuditAction.OPPORTUNITY_CLOSED,
            target=opp
        ))

    return {"status": "closed", "id": opp.id}
```

### 4.2 Error handling

- Services **MUST** raise specific, typed exceptions (e.g., `PermissionDenied`, `InvalidState`, `ValidationError`). Views catch them and map to appropriate HTTP responses.
- No bare `except Exception`; if a transaction must be rolled back, let the exception propagate.
- All exceptions are logged automatically by middleware; services only add context where needed.

### 4.3 Return format

- Services **MUST** return lightweight dictionaries or immutables (`dataclass`, `NamedTuple`). Never ORM objects.
- On success, return at minimum a `{"status": "ok", "id": ...}` or similar. Avoid large nested structures that couple the caller.

---

## 5. Selector Layer Design

### 5.1 Query optimization

Selectors **MUST**:

- Always start from the model’s default manager to enable future changes.
- Use `select_related` for ForeignKey/OneToOne fields needed in the output.
- Use `prefetch_related` for M2M/reverse relationships.
- Apply tenant/scope filters **before** delegation to ensure RBAC data‑level enforcement.

```python
# juxtgo/apps/crm/selectors.py
def get_opportunities_for_user(*, user: User, status: str | None = None) -> list[dict]:
    qs = (
        Opportunity.objects
        .select_related("account_manager", "company")
        .filter(account_manager=user)   # RBAC data scoping
    )
    if status:
        qs = qs.filter(status=status)
    # MUST return list of dicts
    return list(qs.values("id", "title", "status", "company__name", "account_manager__email"))
```

### 5.2 Read-only enforcement

- `selectors.py` **MUST NOT** import `transaction` from `django.db`.
- Writing to the database is **FORBIDDEN** by automated test suite: a memory‑based SQLite test runner verifies that any `INSERT/UPDATE/DELETE` from a selector test fails.
- Caching is **ALLOWED** only if cache keys are generated by helpers and cache operations are idempotent.

---

## 6. Example End‑to‑End Request Lifecycle

**Scenario:** Deactivate a user account (Identity module)

1. **Request** hits `POST /identity/users/42/deactivate/`.
2. **URL dispatcher** maps to `UserDeactivateView` (class‑based view with `PermissionRequiredMixin`).
3. **RBAC check** (coarse): view verifies `request.user.has_perm("identity.change_user")`. If false → 403.
4. **View** extracts `user_id=42` from URL, calls Service:  
   `result = deactivate_user(user_id=42, performed_by=request.user)`.
5. **Service** `deactivate_user`:
   - Re‑validates permission defensively.
   - Opens `transaction.atomic()`.
   - Calls internal _Selector_ to fetch user dict (to confirm existence and current `is_active`).
   - Locks the user row with `select_for_update()`.
   - Sets `is_active=False`, saves.
   - Schedules `on_commit` audit log entry and email notification.
   - Returns `{"status": "deactivated", "user_id": 42}`.
6. **View** receives response, returns `JsonResponse(result)`.

**No layer violated:** Views never touched the User model; Service used a Selector for reads and Models for writes; Selector only read.

---

## 7. Anti‑Patterns with Concrete Examples

### 7.1 “Fat Model” pattern

```python
# ❌ FORBIDDEN
class User(models.Model):
    def send_welcome_email(self):
        ...   # Business logic + I/O inside model
```

**Fix:** Move to `identity/services.py` → `welcome_new_user` service.

### 7.2 View doing business logic

```python
# ❌ FORBIDDEN
def assign_case(request, case_id):
    case = Case.objects.get(id=case_id)
    if request.user.department != "support":
        return HttpResponseForbidden()
    case.assignee = request.user
    case.save()
```

**Fix:** Create `assign_case` service; view merely calls it.

### 7.3 Selector returning ORM for external use

```python
# ❌ FORBIDDEN
def get_all_companies():
    return Company.objects.all()
```

**Fix:** Return `list(Company.objects.values(...))` or a defined dataclass.

### 7.4 Service relying on another Core module’s service directly

```python
# ❌ FORBIDDEN (in CRM service)
from identity.services import get_user_details
```

**Allowed alternative:** CRM’s service calls a Shared module service or an internal event listener.

### 7.5 Skipping RBAC check in view

```python
# ❌ FORBIDDEN
class SecretReportView(View):
    def get(self, request):
        data = get_secret_data()    # No permission check
```

**All views MUST be decorated with `@permission_required("app.action")` or mixin.**

---

**Compliance:** All rules enforced via custom Flake8/pylint checks, pre‑commit hooks, and CI pipeline. No exceptions without Document Owner approval.
