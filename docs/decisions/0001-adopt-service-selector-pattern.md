# ADR-0001: Adopt Service–Selector Pattern

**Date:** 2025-03-12
**Status:** Accepted

## Context

- The codebase is growing; developers mix read and write logic inside views and models.
- We need a uniform way to enforce RBAC and transactional boundaries.
- Read‑side performance suffers from N+1 queries and untestable inline ORM uses.
- Multiple teams need clear ownership of business logic components.

## Decision

> We will separate all business operations into two distinct layers:
>
> - **Services** – stateless functions that handle write operations, enforce permissions, manage transactions, and emit side effects.
> - **Selectors** – plain functions that perform read‑only queries with built‑in RBAC data scoping and return plain dictionaries.
>
> Views become thin glue, never touching the ORM directly.

## Consequences

**Positive:**

- Clear separation of concerns; no more “fat views” or “fat models”.
- Write‑side logic is fully testable without HTTP context.
- Selectors can be cached and routed to read replicas safely.
- RBAC enforcement is consistent and auditable.

**Negative:**

- Verbose initial setup; every module must expose `services.py` and `selectors.py`.
- Cross‑module reuse requires explicit shared interfaces, not ad‑hoc ORM queries.

**Risks / Mitigations:**

- Risk: Developers bypass the pattern due to lack of enforcement.
  Mitigation: Static analysis rules (flake8) and mandatory code review checklist.
- Risk: Performance overhead from dict conversion.
  Mitigation: Use `.values()` and `dataclasses` with no extra overhead; profile before heavy endpoints.

**Affected modules / components:**

- All existing and new modules (identity, crm, workflow) must be refactored.
- Shared modules (audit, notify) remain unchanged.

## Alternatives Considered

| Alternative                                        | Reason Rejected                                                        |
| -------------------------------------------------- | ---------------------------------------------------------------------- |
| Django REST Framework ViewSets with custom actions | Still allowed mixing read/write; no enforced selector layer.           |
| Business logic in model `save()` methods           | Untestable, side‑effect heavy, no control over transaction boundaries. |

## References

- [Backend Architecture Doc](../architecture.md)
- #42 – Refactor identity to Service/Selector
