# JuxtGo OS — Developer Onboarding Guide

**Version:** 1.0  
**Audience:** New backend engineers  
**Enforcement:** All steps are mandatory for local development

This guide gets you from zero to a running JuxtGo OS instance and explains the strict workflow you **MUST** follow.

---

## 1. Requirements

The following tools **MUST** be installed on your development machine:

| Tool           | Version (minimum)                        | Purpose                   |
| -------------- | ---------------------------------------- | ------------------------- |
| Docker         | 24+                                      | Container runtime         |
| Docker Compose | v2 (plugin)                              | Orchestration             |
| Git            | 2.40+                                    | Version control           |
| Python         | 3.11+ (only needed for local venv setup) | Dependencies, linting     |
| pre-commit     | latest                                   | Pre‑commit hooks          |
| curl           | any                                      | Health check verification |

- **Windows users** MUST use WSL2 for all development.
- A code editor with EditorConfig support is strongly recommended (VS Code with Python extensions).

---

## 2. Setup Steps

### 2.1 Clone the Repository

```bash
git clone git@gitlab.example.com:juxtgo/juxtgo-os.git
cd juxtgo-os
```

### 2.2 Environment File

Copy the example environment file and edit secrets (especially `DJANGO_SECRET_KEY` and DB password).  
**Never commit `.env`.**

```bash
cp .env.example .env
# Edit .env: set DJANGO_SECRET_KEY, DB_PASSWORD
```

### 2.3 Docker Setup (Recommended)

This method uses Docker Compose and works identically across macOS, Linux, and WSL2.

```bash
# Build images and start all services in detached mode
docker-compose up -d --build

# Verify running containers
docker-compose ps
```

After the first build, subsequent starts only need `docker-compose up -d` (without build) unless dependencies change.

### 2.4 Local Virtual Environment (Optional)

Only use this if you need to run Django directly (e.g., for IDE debugging). All services except `web` still run via Docker.

```bash
python3 -m venv venv
source venv/bin/activate   # On Windows: venv\Scripts\activate
pip install -r requirements/local.txt
```

Start dependent services:

```bash
docker-compose up -d postgres redis
```

Then run the local Django server:

```bash
DJANGO_SETTINGS_MODULE=juxtgo.settings.development python manage.py runserver
```

---

## 3. Running the Project

### 3.1 First‑time Initialization (inside Docker)

```bash
# Run migrations
docker-compose exec web python manage.py migrate

# Create a superuser (follow prompts)
docker-compose exec web python manage.py createsuperuser

# Collect static files (if not done in Dockerfile)
docker-compose exec web python manage.py collectstatic --noinput
```

### 3.2 Daily Commands

| Action              | Command                                                    |
| ------------------- | ---------------------------------------------------------- |
| Start all services  | `docker-compose up -d`                                     |
| Stop all services   | `docker-compose down`                                      |
| View logs (web)     | `docker-compose logs -f web`                               |
| Access Django shell | `docker-compose exec web python manage.py shell`           |
| Run tests           | `docker-compose exec web pytest`                           |
| Run linting         | `pre-commit run --all-files`                               |
| Load fixtures       | `docker-compose exec web python manage.py loaddata <file>` |

### 3.3 URL Endpoints

- Application: `http://localhost/`
- Django Admin: `http://localhost/admin/`
- Health check: `http://localhost/health/`

---

## 4. Coding Workflow

All feature development follows the same pattern. You **MUST** adhere to the architecture rules (Service‑Selector pattern, RBAC enforcement, etc.). Refer to the **Backend Architecture** document for all constraints.

### 4.1 Adding a New Module

1. Create the module directory under `juxtgo/apps/<module>/` with **all** required subfolders (`models/`, `services/`, `selectors/`, `views/`, `permissions/`, `templates/<module>/`, `migrations/`). See the **Module Structure Standard**.
2. Implement models (one file per model).
3. Implement selectors (read‑only queries, RBAC scoping, return dicts).
4. Implement services (write operations, transactions, RBAC checks, side‑effects).
5. Implement views (class‑based, glue only, `RoleRequiredMixin` if needed).
6. Register URLs with the module’s `app_name` and include in main `urls.py`.
7. Write tests for services and selectors. Tests are mandatory.

### 4.2 Adding a Feature (Inside Existing Module)

1. Create/update service(s) in `<module>/services/<domain>_services.py`.
2. Create/update selector(s) if new reads are required.
3. Create/update view(s) in `<module>/views/<resource>_views.py`.
4. Add permissions to `permissions/permissions.py` if new actions required.
5. Run existing tests and add new ones.

### 4.3 Code Quality Steps (Before Committing)

```bash
# Activate pre-commit hooks
pre-commit install

# Run all checks manually on staged files
pre-commit run
```

This runs:

- `black` (formatting)
- `isort` (import ordering)
- `flake8` (linting, including architecture rules)
- `mypy` (type checking)

**Any failure blocks the commit.**

---

## 5. Git Workflow

### 5.1 Branch Strategy

- `main` – production‑ready branch; **never commit directly**.
- `develop` – integration branch; features branch off from here.
- Feature branches: `type/JUX-###-short-description`.

**Types:** `feat`, `fix`, `refactor`, `docs`, `test`, `chore`, `perf`.

Example: `feat/JUX-147-user-deactivation`

### 5.2 Working on a Feature

```bash
git checkout develop
git pull origin develop
git checkout -b feat/JUX-147-user-deactivation
# ... make changes, commit often ...
git push -u origin feat/JUX-147-user-deactivation
```

### 5.3 Commit Messages

MUST follow: `<type>(<scope>): <imperative description>`

Example: `feat(identity): add deactivate_user service`

- Scope is the module name (e.g., `identity`, `crm`) or `core`.
- No trailing period. Use lowercase.

### 5.4 Pull Requests

1. Open a PR from your branch into `develop`.
2. Assign at least one reviewer.
3. Ensure all CI checks pass (linting, type checking, tests).
4. A reviewer **MUST** pass the **Code Review Checklist** (see Coding Standards doc).
5. Squash merge is used for feature branches.

**Branches without passing CI are rejected.**

---

## 6. Rules to Follow

These rules are enforced automatically; violations lead to broken builds or blocked merges.

- **Architecture rules:** Views never import models. Selectors never write. Services wrap mutations in `transaction.atomic()`. All cross‑module communication via Shared modules or events.
- **RBAC:** Every view/selector/service must check permissions; never assume trust.
- **Templates:** Extend `adminlte/base.html`, use UI Kit components, no business logic.
- **Imports:** Absolute imports only; order: stdlib → third‑party → Django → internal.
- **Commit messages:** Conventional Commits format only.
- **Secrets:** Never commit `.env` or hard‑code credentials.
- **Static analysis:** Pre‑commit hooks MUST pass. CI runs the same checks.
- **Testing:** Every new service and selector MUST have unit tests covering success and error paths.

**Non‑negotiable:** The architecture document is the final authority on patterns. If your solution deviates, stop and discuss with the team before writing code.

---

## 7. Quick Checklist for New Developers

- [ ] Docker installed and running.
- [ ] Repository cloned, `.env` created.
- [ ] Services started with `docker-compose up -d`.
- [ ] Database migrated, superuser created.
- [ ] Able to access `http://localhost/` and `/admin/`.
- [ ] Pre‑commit hooks installed (`pre-commit install`).
- [ ] Understand the module structure and layering (read the Architecture doc).
- [ ] Familiar with branch naming and commit conventions.
- [ ] Know where to find the ADRs for historical decisions.
- [ ] Ready to pick a Jira issue and start coding.

Welcome to JuxtGo OS. Stick to the rules, and your code will sail through review.
