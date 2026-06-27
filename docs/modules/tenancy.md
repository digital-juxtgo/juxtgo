# Tenancy Module – JuxtGo OS

## Overview

The **tenancy** module provides automatic data isolation per organization.
It contains a middleware, a model mixin, and a shared manager.

## Components

### 1. `TenancyMiddleware`

- Reads `current_org_id` from the session
- Stores it in thread‑local storage for the duration of the request

### 2. `TenantManager` (`apps.shared.managers`)

- Custom model manager that automatically filters querysets by the current organization
- Use `objects = TenantManager()` on any tenant‑scoped model

### 3. `TenantQuerysetMixin`

- Model mixin that auto‑assigns `organization_id` when a record is created
- Works automatically when a model inherits from it

## Usage in New Modules

1. Add a `ForeignKey` to `organizations.Organization`.
2. Use `TenantManager` as the default manager.
3. Inherit from `TenantQuerysetMixin` (optional, for auto‑assignment on create).

Example:

```python
class MyModel(BaseModel, TenantQuerysetMixin):
    organization = models.ForeignKey(...)
    objects = TenantManager()
```
