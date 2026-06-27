# CRM Module – JuxtGo OS

**Status:** Complete (v2.0.0)  
**Last updated:** 2025-06-07

---

## Overview

The CRM module provides the core customer relationship management features for JuxtGo OS.  
It is fully tenant‑scoped – every record belongs to an organization and is automatically filtered by `TenantManager`.

### Sub‑modules

- **Companies** – organisations or businesses your agency deals with
- **Contacts** – people associated with a company (or stand‑alone)
- **Pipelines** – sales pipelines with customisable JSON stages
- **Deals** – opportunities linked to a pipeline and company/contact

All CRUD views are built on `BaseListView`, `BaseCreateView`, `BaseUpdateView` from `apps.shared.views.base`.

---

## Data Models

All models inherit from `TenantQuerysetMixin` and use `objects = TenantManager()`.  
They live in `apps/core/crm/models.py`.

### Company

| Field        | Type             | Notes                         |
| ------------ | ---------------- | ----------------------------- |
| id           | UUID (pk)        | from `BaseModel`              |
| organization | FK(Organization) | auto‑set by tenant middleware |
| name         | CharField        | required, max 255             |
| website      | URLField         | optional                      |
| phone        | CharField        | optional                      |
| address      | TextField        | optional                      |
| notes        | TextField        | optional                      |
| created_by   | FK(User)         | auto‑set                      |
| updated_by   | FK(User)         | auto‑set                      |
| created_at   | DateTime         | auto                          |
| updated_at   | DateTime         | auto                          |

- `__str__` returns the company name.
- Manager: `Company.objects` is a `TenantManager`.

### Contact

| Field                                        | Type             | Notes                          |
| -------------------------------------------- | ---------------- | ------------------------------ |
| id                                           | UUID (pk)        | from `BaseModel`               |
| organization                                 | FK(Organization) | auto‑set                       |
| first_name                                   | CharField        | required                       |
| last_name                                    | CharField        | required                       |
| email                                        | EmailField       | required                       |
| phone                                        | CharField        | optional                       |
| company                                      | FK(Company)      | optional, `on_delete=SET_NULL` |
| job_title                                    | CharField        | optional                       |
| notes                                        | TextField        | optional                       |
| (timestamps & audit fields like `BaseModel`) |

- `__str__` returns “first_name last_name”.
- `email` is unique **per tenant** (enforced at the form/service level, not DB constraint).

### Pipeline

| Field        | Type             | Notes                                                         |
| ------------ | ---------------- | ------------------------------------------------------------- |
| id           | UUID (pk)        |                                                               |
| organization | FK(Organization) | auto‑set                                                      |
| name         | CharField        | required                                                      |
| stages       | JSONField        | list of stage objects, e.g. `[{"name":"New","order":1}, ...]` |
| is_default   | BooleanField     | only one default per tenant                                   |
| (timestamps) |                  |                                                               |

- Stages are stored as JSON to allow flexible editing from the UI.

### Deal

| Field        | Type             | Notes                                              |
| ------------ | ---------------- | -------------------------------------------------- |
| id           | UUID (pk)        |                                                    |
| organization | FK(Organization) | auto‑set                                           |
| name         | CharField        | required                                           |
| pipeline     | FK(Pipeline)     | required, `on_delete=PROTECT`                      |
| stage        | CharField        | stores the current stage name (from pipeline JSON) |
| company      | FK(Company)      | optional, `on_delete=SET_NULL`                     |
| contact      | FK(Contact)      | optional, `on_delete=SET_NULL`                     |
| value        | DecimalField     | optional, max_digits=12, decimal_places=2          |
| close_date   | DateField        | optional                                           |
| notes        | TextField        | optional                                           |
| (timestamps) |                  |                                                    |

---

## Selectors

**Path:** `apps/core/crm/selectors.py`

All selectors return **dicts** (never ORM objects). They use `.values()` and chain filters manually because `TenantManager` already scopes the queryset to the current organization.

- `get_company_list()` → list of dicts
- `get_company_detail(pk)` → dict or None
- `get_contact_list(company_id=None)` → list of dicts, optionally filtered by company
- `get_contact_detail(pk)` → dict or None
- `get_pipeline_list()` → list of dicts
- `get_pipeline_detail(pk)` → dict or None
- `get_deal_list(pipeline_id=None, stage=None)` → list of dicts
- `get_deal_detail(pk)` → dict or None

The selectors also compute derived fields if needed (e.g., full contact name, number of deals per company).

---

## Services

**Path:** `apps/core/crm/services.py`

Services handle all write operations. Every mutating method is wrapped in `transaction.atomic()`.

- `create_company(**data)` → returns dict of new company
- `update_company(pk, **data)` → returns updated dict
- `delete_company(pk)` → soft‑delete (if `SoftDeleteModel` used) or hard‑delete; returns `True`
- `create_contact(**data)` → dict
- `update_contact(pk, **data)` → dict
- `delete_contact(pk)` → bool
- `create_pipeline(**data)` → dict
- `update_pipeline(pk, **data)` → dict
- `delete_pipeline(pk)` → bool
- `create_deal(**data)` → dict
- `update_deal(pk, **data)` → dict
- `move_deal(pk, new_stage)` → dict (updates stage field)
- `delete_deal(pk)` → bool

Validation (e.g., unique email per tenant, stage must exist in pipeline JSON) is performed inside the service methods.

---

## Views & URLs

All views live in `apps/core/crm/views/` (separate files per sub‑module) and use the base view classes.

**Namespace:** `core:crm:*`

### Company

| URL name         | Path                               | View                 |
| ---------------- | ---------------------------------- | -------------------- |
| `company_list`   | `/crm/companies/`                  | `BaseListView`       |
| `company_create` | `/crm/companies/create/`           | `BaseCreateView`     |
| `company_edit`   | `/crm/companies/<uuid:pk>/edit/`   | `BaseUpdateView`     |
| `company_delete` | `/crm/companies/<uuid:pk>/delete/` | (POST only, confirm) |

### Contact

| URL name         | Path                              | View             |
| ---------------- | --------------------------------- | ---------------- |
| `contact_list`   | `/crm/contacts/`                  | `BaseListView`   |
| `contact_create` | `/crm/contacts/create/`           | `BaseCreateView` |
| `contact_edit`   | `/crm/contacts/<uuid:pk>/edit/`   | `BaseUpdateView` |
| `contact_delete` | `/crm/contacts/<uuid:pk>/delete/` |                  |

### Pipeline

| URL name          | Path                               | View             |
| ----------------- | ---------------------------------- | ---------------- |
| `pipeline_list`   | `/crm/pipelines/`                  | `BaseListView`   |
| `pipeline_create` | `/crm/pipelines/create/`           | `BaseCreateView` |
| `pipeline_edit`   | `/crm/pipelines/<uuid:pk>/edit/`   | `BaseUpdateView` |
| `pipeline_delete` | `/crm/pipelines/<uuid:pk>/delete/` |                  |

### Deal

| URL name      | Path                           | View             |
| ------------- | ------------------------------ | ---------------- |
| `deal_list`   | `/crm/deals/`                  | `BaseListView`   |
| `deal_create` | `/crm/deals/create/`           | `BaseCreateView` |
| `deal_edit`   | `/crm/deals/<uuid:pk>/edit/`   | `BaseUpdateView` |
| `deal_delete` | `/crm/deals/<uuid:pk>/delete/` |                  |

All views:

- Extend `admin/pages/list.html` or `admin/pages/form.html`.
- Pass context data as dicts from selectors.
- Call service methods on POST.
- Are protected by `LoginRequiredMixin` (via base views) and `RoleRequiredMixin` (appropriate roles can be assigned).

---

## Templates

Templates are stored in `apps/core/crm/templates/crm/` and mirror the sub‑module:

- `company_list.html`, `company_form.html`
- `contact_list.html`, `contact_form.html`
- `pipeline_list.html`, `pipeline_form.html`
- `deal_list.html`, `deal_form.html`

They extend the admin base templates and use AdminLTE components.

---

## Tenant Scoping

- Every model has `organization = models.ForeignKey("organizations.Organization", on_delete=models.CASCADE)`.
- `objects = TenantManager()` on each model ensures querysets always include `filter(organization=current_org)`.
- `TenantQuerysetMixin` (inherited by all models) automatically sets `organization_id` on object creation via `save()`.

---

## Permissions

Default permissions are created automatically by Django:

- `crm.view_company`, `add_company`, `change_company`, `delete_company` (and similarly for contact, pipeline, deal).

Roles can be assigned these permissions via the permissions UI.

---

## Management Commands

### `seed_crm`

**Path:** `apps/core/crm/management/commands/seed_crm.py`

Creates sample data (Companies, Contacts, Pipelines, Deals) for the current organization, useful for development/demo. Only runs if the org has no existing CRM records.

Usage:

```bash
python src/manage.py seed_crm
```
