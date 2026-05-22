# JuxtGo OS – Master Context

## Project Identity
- Name: JuxtGo OS
- Purpose: Modular backend OS for JuxtGo Digital Agency (CRM, billing, etc.)
- Tech: Django 5.0, PostgreSQL, Docker, DRF, SimpleJWT, Wowdash Admin Kit

## Current State (as of 2026-04-24)
- Identity app (`apps.core.identity`):
  - Custom User (email login), Profile, Role models.
  - Services: UserService (register, update, deactivate), AuthService (JWT tokens).
  - Selectors: UserSelector.
  - UI views: login, logout, register, profile self-service, user CRUD (list, create, edit).
  - JWT API: /api/auth/ (register, login, logout, refresh, me).
  - Permissions mixin (RoleRequiredMixin) created but not yet applied to views.
  - Base CRUD classes in `shared/views/base.py`.
- Dashboard app (`apps.dashboard`): home page with user count.
- Wowdash templates: extended in all UI pages, partials for sidebar/navbar/footer.
- Docker: `docker compose up` works, media directory permissions fixed for avatars.

## Key Decisions
- Use Django session auth for dashboard/UI pages (JWT only for external API).
- Keep Django admin as fallback at `/admin/`.
- RBAC will be enabled after core features are stable.
- All new apps shall use `shared.views.base` for CRUD.

## File Locations
- src/apps/core/identity/ (models, services, selectors, views, urls)
- src/apps/dashboard/ (views, urls)
- src/shared/views/base.py (generic CRUD base classes)
- src/templates/admin/ (Wowdash base layout and partials)
- src/config/settings/ (split settings)
- src/config/urls.py
- docker-compose.yml, docker/web/Dockerfile

## Current Focus
[Change this line depending on the chat]