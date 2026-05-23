# JuxtGo OS — DevOps & Deployment Guide

**Document Version:** 1.0  
**Audience:** DevOps Engineers, SRE, Backend Leads  
**Scope:** Local development, staging, and single‑host production deployment

This document describes the containerised runtime, environment configuration, static‑asset serving, logging, health checks, and the standard deployment flow for JuxtGo OS. It assumes familiarity with Docker and Docker Compose.

---

## 1. Docker Architecture

The system is orchestrated via `docker-compose.yml`. All services run in a single Docker network (`juxtgo-net`). Persistent data is stored in named volumes.

```
┌─────────────────────────────────────────────────────────────┐
│                     nginx (ports 80, 443)                   │
│                     reverse proxy, HTTPS offload,           │
│                     serves /static/, /media/                │
└──────────────┬──────────────────────────────────────────────┘
               │ upstream to web:8000
               ▼
┌─────────────────────────────────────────────────────────────┐
│                     web (Django + Gunicorn)                 │
│                     stateless, multiple replicas possible   │
└──────┬────────────────────────────────┬─────────────────────┘
       │                                │
       ▼                                ▼
┌─────────────┐          ┌─────────────────────────┐
│  postgres   │          │         redis           │
│  (primary)  │          │  cache, sessions, queue │
└─────────────┘          └─────────────────────────┘
```

### 1.1 Service Definitions (docker-compose.yml excerpt)

```yaml
version: "3.9"

services:
  web:
    build:
      context: .
      dockerfile: Dockerfile
    image: juxtgo-web:${VERSION:-latest}
    command: gunicorn juxtgo.wsgi:application --bind 0.0.0.0:8000 --workers=3 --access-logfile - --error-logfile -
    environment:
      - DJANGO_SETTINGS_MODULE=juxtgo.settings.production
    env_file:
      - .env
    volumes:
      - static_volume:/app/staticfiles
      - media_volume:/app/media
    depends_on:
      - postgres
      - redis
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8000/health/"]
      interval: 30s
      timeout: 5s
      retries: 3
    restart: unless-stopped

  postgres:
    image: postgres:15-alpine
    environment:
      POSTGRES_DB: ${DB_NAME}
      POSTGRES_USER: ${DB_USER}
      POSTGRES_PASSWORD: ${DB_PASSWORD}
    volumes:
      - pgdata:/var/lib/postgresql/data
    healthcheck:
      test: ["CMD", "pg_isready", "-U", "${DB_USER}"]
      interval: 10s
    restart: unless-stopped

  redis:
    image: redis:7-alpine
    command: redis-server --appendonly yes
    volumes:
      - redisdata:/data
    healthcheck:
      test: ["CMD", "redis-cli", "ping"]
      interval: 10s
    restart: unless-stopped

  nginx:
    image: nginx:alpine
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./deploy/nginx/conf.d:/etc/nginx/conf.d:ro
      - static_volume:/app/staticfiles:ro
      - media_volume:/app/media:ro
      - ./deploy/ssl:/etc/nginx/ssl:ro # if HTTPS is configured
    depends_on:
      - web
    healthcheck:
      test: ["CMD", "nginx", "-t"]
      interval: 30s
    restart: unless-stopped

volumes:
  pgdata:
  redisdata:
  static_volume:
  media_volume:
```

- **web** is built from the project’s `Dockerfile` (multi‑stage build recommended). It uses Gunicorn in production, logging to stdout/stderr.
- **postgres** and **redis** use official images with persistent volumes.
- **nginx** handles external HTTP traffic and serves `/static/` and `/media/` directly, bypassing Django.

---

## 2. Environment Management

All non‑image configuration is injected via a single `.env` file at the project root (excluded from VCS). Docker Compose reads this file automatically.

### 2.1 .env Structure

```
# ── Django ───────────────────
DJANGO_SECRET_KEY=unsafe-dev-only-change-this
DJANGO_DEBUG=False
DJANGO_ALLOWED_HOSTS=example.com,www.example.com

# ── Database (PostgreSQL) ────
DB_NAME=juxtgo
DB_USER=juxtgo_user
DB_PASSWORD=strong-db-password

# ── Redis ────────────────────
REDIS_URL=redis://redis:6379/1

# ── Email ────────────────────
EMAIL_HOST=smtp.example.com
EMAIL_PORT=587
EMAIL_HOST_USER=noreply@example.com
EMAIL_HOST_PASSWORD=mail-password
EMAIL_USE_TLS=True

# ── Storage ──────────────────
STATIC_ROOT=/app/staticfiles
MEDIA_ROOT=/app/media

# ── Optional: Sentry DSN ────
SENTRY_DSN=https://...@sentry.io/...
```

**Rules:**

- Every variable required by `settings/production.py` **MUST** be defined.
- `DJANGO_SECRET_KEY` **MUST** be a cryptographically strong value generated with:  
  `python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"`
- The `.env` file **MUST NOT** be committed to version control. An `.env.example` template without secrets is maintained instead.

### 2.2 Environment Overrides

For multi‑environment setups, create separate `.env.staging`, `.env.prod`. Use `docker-compose -f docker-compose.yml --env-file .env.prod up -d`. Never use the same secret across environments.

---

## 3. Static & Media Handling

### 3.1 Static Files (AdminLTE, module assets)

- In production, Django never serves static files.
- `STATIC_ROOT = "/app/staticfiles"` inside the web container.
- `python manage.py collectstatic --noinput` collects everything into that directory.
- The `static_volume` is mounted to both `web` and `nginx`.  
  Nginx location block:
  ```nginx
  location /static/ {
      alias /app/staticfiles/;
      expires 30d;
      add_header Cache-Control "public, immutable";
  }
  ```
- During build, `collectstatic` can be run in the Dockerfile (optional, but then assets are baked into the image; volume mount overrides if needed).

### 3.2 Media Files (user uploads, avatars)

- `MEDIA_ROOT = "/app/media"` shared via mounted volume.
- Nginx serves `/media/` similarly:
  ```nginx
  location /media/ {
      alias /app/media/;
  }
  ```
- In development, Django handles media via `settings.DEBUG=True` additions, but `MEDIA_ROOT` volume ensures persistence.

### 3.3 S3 / Cloud Storage (future)

For multi‑host deployment, the volume model breaks down. The document expects a migration to `django-storages` with S3. Until then, single‑host volume‑based storage is the standard.

---

## 4. Logging Strategy

All application logs are structured as JSON and written to **stdout** / **stderr**. Docker’s logging driver captures them, and they can be forwarded to a central sink (ELK, Datadog, etc.) by the container runtime.

### 4.1 Django Production Logging Configuration

```python
LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "json": {
            "()": "pythonjsonlogger.jsonlogger.JsonFormatter",
            "format": "%(asctime)s %(name)s %(levelname)s %(message)s",
        },
    },
    "handlers": {
        "console": {
            "class": "logging.StreamHandler",
            "stream": "ext://sys.stdout",
            "formatter": "json",
        },
    },
    "root": {
        "handlers": ["console"],
        "level": "INFO",
    },
    "loggers": {
        "django": {"level": "INFO"},
        "gunicorn.access": {
            "handlers": ["console"],
            "level": "INFO",
            "propagate": False,
        },
    },
}
```

- Gunicorn access/error logs go to stdout (configured via command line).
- PostgreSQL and Redis logs are written to stdout by the official images.

### 4.2 Container Logging

- Docker logs can be viewed with `docker-compose logs -f web`.
- For production, configure a logging driver like `fluentd`, `journald`, or `awslogs` in `docker-compose.override.yml`.

---

## 5. Health Checks

All services implement Docker health checks that monitor core functionality, not just process existence.

### 5.1 /health/ Endpoint (Django)

The web service exposes a `/health/` endpoint that verifies database and Redis connectivity:

```python
# In a core app views
def health_check(request):
    from django.db import connections
    from django_redis import get_redis_connection
    try:
        connections["default"].cursor()
        get_redis_connection("default").ping()
    except Exception:
        return JsonResponse({"status": "unhealthy"}, status=503)
    return JsonResponse({"status": "ok"})
```

### 5.2 Container Health Checks

- **postgres:** `pg_isready -U $DB_USER`
- **redis:** `redis-cli ping`
- **nginx:** `nginx -t` (configuration test) – not ideal for runtime, but catches misconfigurations; an additional active check could verify a static file response.
- **web:** `curl -f http://localhost:8000/health/`

Docker Compose’s `healthcheck` ensures service dependencies are started only when healthy.

---

## 6. Deployment Flow

The standard deployment flow assumes a single‑host setup with Docker Compose. A CI/CD pipeline would execute these steps.

### 6.1 Pre‑requisites

- Target server: Docker CE and `docker-compose-plugin` installed.
- `git` access to repository.
- `.env.prod` file present on the server (never in source repo).

### 6.2 Step‑by‑Step Deployment

**1. Build or Pull Images**

```bash
# Option A: Build locally and push to registry (recommended for multi‑server)
docker-compose -f docker-compose.yml build web
docker tag juxtgo-web:latest registry.example.com/juxtgo-web:$VERSION
docker push registry.example.com/juxtgo-web:$VERSION

# On target server:
docker-compose -f docker-compose.prod.yml pull
```

**Option B:** Build directly on the server (simpler for single host)

```bash
docker-compose -f docker-compose.yml build --pull web
```

**2. Stop Old Containers (if running) and Start New**

```bash
docker-compose down --remove-orphans   # stops services, removes orphan containers
docker-compose up -d --force-recreate  # pulls if needed, recreates, detached mode
```

**3. Run Database Migrations**

```bash
docker-compose exec web python manage.py migrate --noinput
```

**4. Collect Static Files**

```bash
docker-compose exec web python manage.py collectstatic --noinput --clear
```

- This re‑collects all static assets into the shared volume, ensuring Nginx serves the latest version.

**5. Verify Deployment**

```bash
curl -f http://localhost/health/    # should return {"status":"ok"}
```

**6. Post‑Deployment Checks**

- Check container logs: `docker-compose logs --tail=50 web`
- Ensure all services report healthy: `docker-compose ps`

### 6.3 Rollback

To roll back to a previous image tag:

```bash
export VERSION=1.2.3
docker-compose pull
docker-compose up -d --force-recreate
# then migrate only if schema changes were reverted (minimal risk)
```

### 6.4 Database Backups (cron job)

A daily backup of PostgreSQL is executed via:

```bash
docker-compose exec -T postgres pg_dump -U $DB_USER $DB_NAME | gzip > backup_$(date +%F).sql.gz
```

---

## 7. Production Dockerfile Overview

A minimal multi‑stage `Dockerfile`:

```dockerfile
# Build stage for Python dependencies
FROM python:3.11-slim AS builder
RUN apt-get update && apt-get install -y --no-install-recommends gcc libpq-dev && rm -rf /var/lib/apt/lists/*
WORKDIR /app
COPY requirements.txt .
RUN pip wheel --no-cache-dir --wheel-dir /wheels -r requirements.txt

# Final stage
FROM python:3.11-slim
RUN apt-get update && apt-get install -y --no-install-recommends libpq-dev curl && rm -rf /var/lib/apt/lists/*
WORKDIR /app
COPY --from=builder /wheels /wheels
RUN pip install --no-cache /wheels/*
COPY . .
RUN python manage.py collectstatic --noinput   # optional, can be done at runtime
EXPOSE 8000
CMD ["gunicorn", "juxtgo.wsgi:application", "--bind", "0.0.0.0:8000", "--workers=3"]
```

---

## 8. Security Notes

- Database credentials and secrets are **never** passed as command‑line arguments or baked into images.
- All inter‑service communication runs inside the isolated Docker network; PostgreSQL and Redis ports are **not** exposed to the host.
- Nginx must serve all public traffic and terminate HTTPS (SSL certificates mounted as secrets or issued via Let’s Encrypt).
- Regular image rebuilding ensures OS‑level security patches (base images upgraded via `--pull` on build).

---

**Document maintainer:** DevOps Lead / Platform Engineer  
**Review cycle:** After any infrastructure change or quarterly.

## Adding a New Core App

When you create a new app (e.g., `organizations`), you must:

1. Add it to `INSTALLED_APPS` in `config/settings/base.py`
2. Rebuild the Docker image:
   ```bash
   docker compose down
   docker compose up -d --build
   ```
