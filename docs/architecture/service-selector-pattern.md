# JuxtGo OS — The Service–Selector Pattern

**Document Version:** 1.1  
**Audience:** Backend Engineers, Platform Architects  
**Context:** Must be read after the _Strict Backend Architecture_ document.

---

## 1. Why This Pattern Exists

The Service–Selector pattern is a **domain‑oriented CQRS‑lite** enforcement mechanism. It exists to solve these real‑world problems in a growing Django monolith:

- **Write operations are fundamentally different from reads.** Writes require transactions, permission checks, side effects (email, audit log), and state validation. Reads benefit from optimised queries, caching, and composability. Mixing them (e.g., in a single view or model method) creates god objects that are impossible to test or optimise independently.

- **Codebase scalability across multiple teams.** Without a mandatory separation, developers default to dumping logic into views or models. This leads to _fat views_ that touch the ORM directly, duplication of business rules, and poor visibility of what the system actually does.

- **Enforceable RBAC and data scoping.** Permission checks must happen **twice** — once at the coarse HTTP layer (view), and again at the data level (which records the current user can see). Selectors apply role‑based row‑level security automatically; services perform defensive permission checks before mutating state. By forcing all reads through Selectors and all writes through Services, no code path can accidentally leak data or bypass authorisation.

- **Transformational safety.** Services are stateless, transactional units that either succeed completely or roll back. Selectors are read‑only and idempotent. The separation means you can deploy read replicas, add aggressive caching, or even replace the read side with a search index **without touching business logic**.

- **Testability.** Services can be tested in isolation (passing in mock permissions, inputs) without a full HTTP context. Selectors can be tested with known database fixtures and verify RBAC filtering. Views become thin glue tested mostly via integration.

---

## 2. Service Layer

### 2.1 Responsibilities

- **Encapsulate all write‑side business rules.** State transitions, integrity checks, multi‑object coordination.
- **Enforce coarse + fine‑grained RBAC.** Every service function **MUST** re‑verify that the acting user has the correct permission.
- **Control transactions.** `transaction.atomic()` is the **only** place transactions are opened; services never leave a transaction hanging.
- **Emit side effects after commit.** Audit log entries, email sending, or push notifications must be deferred by `transaction.on_commit()` to guarantee they fire only after the database change is durable.
- **Return lightweight results.** Always plain `dict`, `dataclass`, or `None` — never ORM objects.

### 2.2 Function Structure

```python
def <action>_<entity>(*, <inputs>, performed_by: User) -> dict:
    # 1. Permission check (decorator or inline)
    if not performed_by.has_perm("<app>.<action>_<model>"):
        raise PermissionDenied

    # 2. Optional: fetch required data via Selectors
    existing = some_selector_func(user=performed_by, ...)

    # 3. Transactional block
    with transaction.atomic():
        # - Selectors for data scoping if needed
        # - select_for_update() for row locking
        # - Business rule checks
        # - Model updates
        # - Defer side effects
        transaction.on_commit(lambda: audit.log(...))
        transaction.on_commit(lambda: notify.send_email(...))

    return {"status": "success", "id": obj.pk}
```

**Crucial rule:** The service **MUST NOT** call `Model.objects.get/filter` directly to fetch objects it modifies; it uses either the same module’s internal selector or a shared module’s selector to guarantee RBAC + data scoping.

### 2.3 Return Format & Error Handling

- Success returns: `{"status": "ok", ...}` or a dedicated dataclass.
- Errors raise **typed exceptions**: `PermissionDenied`, `ValidationError`, `InvalidState`, `NotFound`. These are caught by middleware and converted to appropriate HTTP 4xx/5xx.
- Never `return None` to indicate failure; always raise.

### 2.4 Example: Deactivate User

```python
# identity/services/account_services.py
def deactivate_user(*, user_id: int, performed_by: User) -> dict:
    if not performed_by.has_perm("identity.change_user"):
        raise PermissionDenied

    from ..selectors.user_selectors import get_user_by_id  # internal to module

    with transaction.atomic():
        user = User.objects.select_for_update().get(pk=user_id)
        # defensive check
        if not user.is_active:
            raise InvalidState("User already deactivated.")

        user.is_active = False
        user.save(update_fields=["is_active"])

        transaction.on_commit(lambda: audit_log(actor=performed_by, action="DEACTIVATE", target_id=user.id))
        transaction.on_commit(lambda: send_deactivation_email(user.email))

    return {"status": "deactivated", "user_id": user.id}
```

---

## 3. Selector Layer

### 3.1 Responsibilities

- **Read‑only data retrieval.** Absolutely no INSERT/UPDATE/DELETE.
- **Composable, optimised QuerySets.** Use `select_related`, `prefetch_related`, `only`, `defer` as needed.
- **Automatic RBAC data scoping.** Every selector **MUST** apply the role‑based filters that restrict which rows the requestor can see. For example, a sales rep `get_opportunities` selector filters by `account_manager=requestor`.
- **Return plain Python structures.** `list[dict]`, `dict`, custom dataclasses. **NEVER** return ORM objects to callers outside the module.
- **Optional caching.** Selectors may use Redis cache with cache‑aside for expensive read models, but invalidation must be explicitly designed.

### 3.2 Query Patterns

```python
# identity/selectors/user_selectors.py
from django.core.cache import cache

def get_active_users(*, company_id: int, requestor: User) -> list[dict]:
    if not requestor.has_perm("identity.view_user"):
        raise PermissionDenied

    qs = (
        User.objects
        .filter(company_id=company_id, is_active=True)
        .select_related("profile")
        .only("id", "email", "display_name", "profile__avatar")
    )
    return list(qs.values("id", "email", "display_name", "profile__avatar"))

def get_user_by_id(*, user_id: int, requestor: User) -> dict:
    if not requestor.has_perm("identity.view_user"):
        raise PermissionDenied

    # Scoped query: the requestor must belong to the same company (example rule)
    cached = cache.get(f"user:{user_id}")
    if cached and cached.get("company_id") == requestor.company_id:
        return cached

    user = (
        User.objects
        .filter(pk=user_id, company_id=requestor.company_id)
        .values("id", "email", "display_name", "is_active", "company_id")
        .first()
    )
    if user:
        cache.set(f"user:{user_id}", user, 300)
    return user
```

### 3.3 Performance Considerations

- Selectors **MUST** be profiled for N+1 queries; using `select_related`/`prefetch_related` is mandatory.
- All querysets are lazy; final conversion to list/dict forces evaluation.
- Data scoping filters **MUST** be used early to reduce the result set before complex joins.
- Caching is **ALLOWED** but must never become a source of stale data that breaks business rules (e.g., permission changes must invalidate relevant cached selectors).

---

## 4. Interaction Rules

| From → To                         | ALLOWED?                      | Rationale                                                                                        |
| --------------------------------- | ----------------------------- | ------------------------------------------------------------------------------------------------ |
| Service → Selector (same module)  | **YES**                       | Service needs read data; using Selectors guarantees RBAC scoping and avoids direct ORM coupling. |
| Service → Selector (other module) | **NO** (unless Shared module) | Core modules communicate only through Shared modules or events.                                  |
| Selector → Service                | **FORBIDDEN**                 | Reads must be free of side effects; writes never trigger on a read path.                         |
| Selector → Model                  | **YES**                       | Internal QuerySet construction, but never exposed externally.                                    |
| View → Service                    | **YES**                       | For mutations.                                                                                   |
| View → Selector                   | **YES**                       | For rendering.                                                                                   |
| View → Model                      | **FORBIDDEN**                 | Static analysis rule.                                                                            |

**Rationale:** The separation ensures that any piece of code that modifies state is a Service. Any code that reads is a Selector. There is no ambiguous “manager” layer that does both.

---

## 5. Full Example: Create + Fetch a Company

**Create (write):**

```python
# crm/services/company_services.py
def create_company(*, name: str, owner_id: int, performed_by: User) -> dict:
    if not performed_by.has_perm("crm.add_company"):
        raise PermissionDenied

    from ..selectors.company_selectors import get_company_by_name

    with transaction.atomic():
        if get_company_by_name(name=name, requestor=performed_by):  # internal check
            raise ValidationError("Company name exists.")
        company = Company.objects.create(name=name, owner_id=owner_id)
        transaction.on_commit(lambda: audit_log(actor=performed_by, action="CREATE_COMPANY", target_id=company.id))
    return {"status": "created", "company_id": company.id}
```

**Fetch (read):**

```python
# crm/selectors/company_selectors.py
def get_company_detail(*, company_id: int, requestor: User) -> dict:
    if not requestor.has_perm("crm.view_company"):
        raise PermissionDenied

    # Scoping: e.g., requestor must have access based on team hierarchy
    return (
        Company.objects
        .filter(pk=company_id, allowed_users=requestor)  # fictional RBAC filter
        .select_related("owner")
        .values("id", "name", "owner__email", "created_at")
        .first()
    )
```

**View (thin glue):**

```python
class CompanyCreateView(PermissionRequiredMixin, View):
    permission_required = "crm.add_company"

    def post(self, request):
        result = create_company(
            name=request.POST["name"],
            owner_id=request.user.id,
            performed_by=request.user
        )
        return JsonResponse(result)
```

All interaction is stateless, testable, and auditable.

---

## 6. Anti-Patterns & Consequences

### 6.1 Fat View

```python
# ❌ FORBIDDEN
def toggle_active(request, user_id):
    user = User.objects.get(pk=user_id)          # ORM in view
    if not request.user.is_superuser:            # inline permission check
        return HttpResponseForbidden()
    user.is_active = not user.is_active
    user.save()
    return redirect(...)
```

**Impact:** Business logic is unreusable (can’t call from a management command or API), untestable without HTTP, and bypasses standardised RBAC.

### 6.2 Logic Duplication (Service bypassed)

```python
# In a different view, same logic is copied
def deactivate_from_bulk_action(request):
    for uid in request.POST.getlist("ids"):
        user = User.objects.get(pk=uid)
        user.is_active = False
        user.save()
```

**Impact:** No audit trail, no transaction safety, no permission check – and any change to the deactivation rules must be updated in multiple places.

### 6.3 Selector That Writes

```python
# ❌ FORBIDDEN
def get_latest_orders(requestor):
    if not cache.get(...):
        orders = Order.objects.filter(...)
        cache.set(...)            # cache write, okay
        # Oops: also logs a view event
        ActivityLog.objects.create(...)   # WRITE! Breaks read-only promise
    ...
```

**Impact:** A read‑only query suddenly mutates the audit log, causing deadlocks in read replicas, unpredictable side effects, and makes caching layers impossible.

### 6.4 Service Calling Another Core Module’s Service

```python
# ❌ In CRM service
from identity.services import create_user
```

**Impact:** Tight coupling, testing nightmares, and blocks independent module releases. Instead, use shared interfaces or events.

---

## 7. Scaling Implications

The Service–Selector separation directly enables:

- **Read replica offloading:** Because Selectors are explicitly read‑only, they can be routed to read replicas via database routers, without any risk of accidental writes.

- **Caching layer insertion:** A Selector’s return values can be cached in Redis. Since the Selector is guaranteed not to cause side effects, you can cache aggressively. Invalidation hooks live alongside the Services that modify the data (Service → `transaction.on_commit(...cache.delete(...))`).

- **Background job reuse:** Services are plain functions, callable from Celery workers with zero HTTP coupling. A management command can reuse the exact same `create_company` service.

- **CQRS migration path:** If in the future we need to project read models into ElasticSearch, the Selector layer can be replaced with a search query while keeping the Service layer unchanged. The architecture is decoupled.

- **Horizontal scaling of Django instances:** Stateless Services and Selectors simply scale out with more Gunicorn workers, because state lives in the database and cache. No sticky sessions needed.

- **Granular testing:** Each Service can be integration‑tested against a database. Each Selector can be tested with a fixture set to assert RBAC filtering. The test pyramid remains flat and fast.

---

**Enforcement:** All new modules and refactors **MUST** adhere to the Service–Selector pattern. Pull requests that mix reads with writes, put business logic into views or models, or bypass Selectors will be rejected automatically by static analysis tools.
