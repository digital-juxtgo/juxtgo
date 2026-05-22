# JuxtGo OS

[![CI](https://github.com/digital-juxtgo/juxtgo/actions/workflows/ci.yml/badge.svg)](https://github.com/digital-juxtgo/juxtgo/actions)

Modular multi-tenant SaaS platform built with Django 5, PostgreSQL, Docker, and AdminLTE 3.2.

## 🧱 Architecture

- **Service/Selector Pattern** – clean separation of read/write logic
- **Multi-tenant** – organization-scoped data isolation
- **Modular monolith** – shared core, independent business domains

## 🚀 Quick Start

```bash
cp .env.example .env
docker compose up --build
docker compose exec web python manage.py migrate
docker compose exec web python manage.py seed_roles
docker compose exec web python manage.py createsuperuser
```
