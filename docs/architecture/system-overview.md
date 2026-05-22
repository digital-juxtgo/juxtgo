# JuxtGo OS — System Overview

**Document Version:** 2.0  
**Audience:** Platform Engineers, Backend Developers  
**Last Updated:** 2026-05-01

---

## 1. System Purpose

JuxtGo OS is a **production-grade, modular business platform** built as a **Django monolithic application**. It serves as the backbone for internal tools, customer management, identity services, and extensible business workflows. The platform enforces strict architectural boundaries to guarantee maintainability, auditability, and consistent RBAC enforcement across all modules.

---

## 2. High-Level Architecture Diagram

```
                    ┌─────────────────────────────────────────┐
                    │             Nginx (Reverse Proxy)        │
                    │   - Static files (AdminLTE assets)       │
                    │   - SSL termination                      │
                    └─────────────┬───────────────────────────┘
                                  │
                                  ▼
                    ┌─────────────────────────────────────────┐
                    │       Django Application (Monolith)       │
                    │  ┌────────────┐  ┌────────────┐          │
                    │  │  Core      │  │  Shared    │          │
                    │  │  Modules   │  │  Modules   │          │
                    │  │  - Identity│  │  - UI Kit  │          │
                    │  │  - CRM     │  │  - Audit   │          │
                    │  │  - ...     │  │  - Notify  │          │
                    │  └────────────┘  └────────────┘          │
                    │  Layers: Templates → Views → Services →  │
                    │           Selectors / Models             │
                    └──────┬──────────────────┬───────────────┘
                           │                  │
            ┌──────────────▼──┐    ┌──────────▼──────────┐
            │   PostgreSQL    │    │       Redis          │
            │   (Primary DB)  │    │  (Cache / Sessions / │
            │                 │    │   Background queues) │
            └─────────────────┘    └─────────────────────┘
                    ▲
                    │
           ┌────────┴───────┐
           │  Docker Compose│
           │ (dev & prod)   │
           └────────────────┘
```

- **Nginx** serves static AdminLTE assets and proxies API/template requests.
- **Django** houses all business logic in a strict layered architecture.
- **PostgreSQL** is the single source of truth.
- **Redis** is used for caching, session storage, and as a backend for Celery task queues.

---

## 3. Core Architectural Principles

| Principle                    | Enforced Rule                                                                                                                                                                                                                                                                                                                                       |
| ---------------------------- | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| **Modular Design**           | Each Django app is a self‑contained module in `juxtgo/apps/<module>/`. Modules expose public APIs only through declared `services.py` and `selectors.py`. Cross‑module imports outside these files are forbidden.                                                                                                                                   |
| **Separation of Concerns**   | Strict 5‑layer stack: Templates, Views, Services, Selectors, Models. No layer may skip or bypass the one directly below it. Views never touch Models directly.                                                                                                                                                                                      |
| **Service–Selector Pattern** | Write operations (create/update/delete) live in **Services**; read operations live in **Selectors**. Services orchestrate business logic, validate permissions, and enforce transactional consistency. Selectors return plain values (dicts, dataclasses) — never ORM objects across module boundaries.                                             |
| **RBAC Enforcement**         | All permissions derive from Django’s built‑in `Permission` model, grouped into **Roles** (via `Group`). Every View must perform a `request.user.has_perm()` check (wrapped by custom decorator) before dispatching to a Service or Selector. Data‑level scoping is achieved through Selector‑level filtering that respects the role’s tenant/scope. |

---

## 4. Layered Architecture Explanation

```
┌────────────────────────────────────────────────────────────────┐
│                         TEMPLATES                              │
│  AdminLTE‑based Jinja2 templates; use reusable components      │
│  (cards, tables, forms). No business logic in templates.       │
├────────────────────────────────────────────────────────────────┤
│                           VIEWS                                │
│  Django class‑based views (or thin function views).            │
│  Responsibilities:                                             │
│  - Parse request, call RBAC decorator                          │
│  - Delegate to Service (mutations) or Selector (reads)         │
│  - Map result to template context or JSON response             │
│  Strict rule: Views never import Models directly.              │
├────────────────────────────────────────────────────────────────┤
│                         SERVICES                               │
│  Plain Python classes/functions in services.py.                │
│  - Encapsulate all business logic and state transitions.       │
│  - Trigger model saves, emit events, launch async tasks.       │
│  - Validate permissions again (defensive check).               │
│  - Transactions: use `transaction.atomic()` at the service     │
│    entry point, never inside selectors.                        │
│  - Return nothing or a lightweight result dataclass.           │
├────────────────────────────────────────────────────────────────┤
│                        SELECTORS                               │
│  Plain Python functions in selectors.py.                       │
│  - Composable, optimized QuerySets (select_related,            │
│    prefetch_related).                                          │
│  - Apply RBAC data‑scoping automatically (filter by tenant,    │
│    role‑based field visibility).                               │
│  - Return dicts, lists, or well‑defined dataclasses.           │
│    NEVER return ORM objects to the caller (View or Template).  │
├────────────────────────────────────────────────────────────────┤
│                          MODELS                                │
│  Django ORM models, signals stripped or used only for low‑level│
│  internal triggers (e.g., audit log creation).                 │
│  - No business logic in methods (save/delete overrides only    │
│    for data integrity).                                        │
│  - Foreign keys across modules must point through abstract     │
│    interfaces defined in shared modules (to avoid hard         │
│    coupling).                                                  │
└────────────────────────────────────────────────────────────────┘
```

**Examples:**

_Selector (identity/selectors.py)_

```python
def get_user_by_email(*, email: str, requestor: User) -> dict:
    if not requestor.has_perm("identity.view_user"):
        raise PermissionDenied
    return (
        User.objects.filter(email=email)
        .values("id", "email", "display_name", "is_active")
        .first()
    )
```

_Service (identity/services.py)_

```python
@transaction.atomic
def deactivate_user(*, user_id: int, performed_by: User):
    if not performed_by.has_perm("identity.change_user"):
        raise PermissionDenied
    user = User.objects.select_for_update().get(id=user_id)
    user.is_active = False
    user.save(update_fields=["is_active"])
    audit_service.log_event(actor=performed_by, action="USER_DEACTIVATED", target=user)
    notify_service.send_deactivation_email(user.email)
    return {"status": "deactivated"}
```

_View (identity/views.py)_

```python
class UserDeactivateView(PermissionRequiredMixin, View):
    permission_required = "identity.change_user"

    def post(self, request, user_id):
        result = deactivate_user(user_id=user_id, performed_by=request.user)
        return JsonResponse(result)
```

---

## 5. Module Classification

### Core Modules

These are business‑critical, cannot be disabled, and define the platform’s primary data domains.

| Module       | Purpose                                  | Key Dependencies            |
| ------------ | ---------------------------------------- | --------------------------- |
| **Identity** | User lifecycle, RBAC, authentication     | Shared.Audit, Shared.Notify |
| **CRM**      | Contact, Company, Opportunity management | Identity, Shared.Audit      |
| **Workflow** | Custom approval flows, state machines    | Identity, Shared.Notify     |

### Shared Modules

Provide cross‑cutting infrastructure; no business logic.

| Module     | Purpose                                               | Used By                      |
| ---------- | ----------------------------------------------------- | ---------------------------- |
| **UI Kit** | AdminLTE overrides, reusable template tags, mixins    | All templates                |
| **Audit**  | Immutable audit log (ActivityLog model)               | All services                 |
| **Notify** | Email/SMS/In‑app notification abstraction             | Services that trigger alerts |
| **API**    | Shared utilities for REST API serialization (if used) | API‑only views               |

**Rule:** Core modules may depend on Shared modules, but **never** on another Core module directly. Communication between Core modules must happen through events (Django signals with synchronous dispatchers within the same process) or via a well‑defined service interface in a Shared module.

---

## 6. Data Flow — Full Request Lifecycle

```
Incoming HTTP Request
        │
        ▼
┌───────────────────┐
│  Nginx            │
│  SSL termination, │
│  static files     │
└───────┬───────────┘
        │
        ▼
┌───────────────────────────────────────────┐
│  Django URL Router                         │
│  Matches URL → view class/function         │
└───────┬───────────────────────────────────┘
        │
        ▼
┌───────────────────┐
│  View Middleware   │
│  - Authentication  │
│  - RBAC decorator  │   ← request.user.has_perm() enforced
│  - Transaction     │     (non‑atomic reads, atomic writes)
└───────┬───────────┘
        │
        ├─ READ request ──────────────────────────┐
        │                                         │
        │                                         ▼
        │        ┌─────────────────────────────────────┐
        │        │  Selector function                   │
        │        │  - Applies role‑based data filtering │
        │        │  - Returns dict / dataclass          │
        │        └───────────────┬─────────────────────┘
        │                        │
        │                        ▼
        │             Template rendering (AdminLTE)
        │             or JSON response
        │
        ├─ WRITE request ─────────────────────────┐
        │                                         │
        │                                         ▼
        │        ┌───────────────────────────────────────┐
        │        │  Service function (transaction.atomic)│
        │        │  - Business rules, validation         │
        │        │  - ORM operations via .save()         │
        │        │  - Audit log entry                    │
        │        │  - Post‑commit tasks (Celery or sync) │
        │        └───────────────┬───────────────────────┘
        │                        │
        │                        ▼
        │             Redirect / JSON success response
        │
        └────────────────────────────────────────
```

- **RBAC** is checked twice: once by the view decorator (coarse‑grained), and optionally inside the Selector/Service for data‑level scoping.
- **Transactions** are controlled exclusively at the Service layer. Selectors never start transactions; they run in autocommit mode for read consistency.
- All responses (HTML or JSON) are rendered after the View receives data from the lower layers.

---

## 7. Non‑Functional Priorities

### Scalability

- Read‑heavy endpoints rely on **Selectors** with `QuerySet` optimizations that hit database replicas (if configured).
- **Redis** caches frequently‑used selector results (e.g., permissions matrix) with cache‑aside pattern; invalidation via `post_save` signals.
- The monolith can be scaled horizontally by replicating the **Docker container** behind `Nginx`, provided statelessness is maintained (sessions in Redis).

### Maintainability

- **Enforced layering** prevents leaky abstractions. Static analysis (custom lint rule) ensures no `from app.models import *` inside views.
- **Service–Selector** split gives unambiguous “where to place code” rules. Each module has exactly one `services.py` and one `selectors.py`.
- **Module classification** (Core vs Shared) prevents circular dependencies. Any violation breaks imports at build time.

### Security

- **RBAC** is not optional; every view is gated. Permission names follow `<app>.<action>_<model>` convention.
- All user inputs are validated at the **View** boundary (Django forms or DRF serializers), then passed clean to Services.
- **Audit log** captures every state‑changing action with actor, timestamp, and target; it is append‑only and queried through a dedicated Selector.
- Docker deployment enforces no root database access, secrets managed via environment variables (in `.env` files not committed to VCS).
