Below is a **structured system snapshot** of JuxtGo and a **production-grade prompt pack** to execute up to **Phase 2** without architectural drift.

---

# 1. JuxtGo — System Summary

## 1.1 Identity

**JuxtGo** is a **multi-venture digital platform ecosystem** built on a shared internal framework:

* **JuxtGo OS** → Core modular backend (Django-based system)
* **JuxtGo Digital** → Agency layer (client projects powered by OS)
* **Product Ventures** → e.g.

  * JuxtGo Mart
  * JuxtGo Travel

---

## 1.2 Strategic Objective

Build a **reusable, scalable, modular backend platform** that:

* avoids monolithic coupling
* enables rapid product launches
* enforces architectural consistency
* supports multi-tenant and multi-domain systems

---

## 1.3 Core Architecture Philosophy

### Principles

* Modular Django apps (feature-based, not generic)
* Clean architecture (separation of concerns)
* Service layer pattern
* Infrastructure-aware design (Docker-first)
* Database-first thinking (PostgreSQL optimized)
* Future-proof (multi-tenant ready)

---

## 1.4 Technology Stack

| Layer      | Tech                                 |
| ---------- | ------------------------------------ |
| Backend    | Django + DRF                         |
| Database   | PostgreSQL                           |
| Cache      | Redis                                |
| Deployment | Docker + Docker Compose              |
| Proxy      | Nginx                                |
| Versioning | Git                                  |
| Frontend   | WowDash (admin template integration) |

---

# 2. What Has Been Done (Current State)

Based on your work so far:

## 2.1 Environment Setup

* Python virtual environment configured
* Django project initialized
* PostgreSQL integration attempted (issues encountered but progressing)
* Git + SSH setup in progress

---

## 2.2 Dockerization (In Progress)

* Dockerfile standardization started
* Docker Compose partially configured
* Build issues identified (not yet stabilized)

---

## 2.3 Core App Initialization

* Initial app created:

  * `identity` module
* Custom user model introduced
* Migrations created
* Migration execution facing DB issues (PostgreSQL config)

---

## 2.4 Architectural Direction (Defined but not fully implemented)

You have already decided:

* Modular app structure:

  ```
  apps/
    core/
    shared/
    features/
  ```

* Clean layering intention:

  * models
  * services
  * APIs
  * permissions

* Admin UI:

  * WowDash planned for integration

---

## 2.5 Gaps (Critical)

These are not fully completed yet:

* Stable Docker environment
* Base app template (reusable module pattern)
* Service layer enforcement
* Config separation (dev/staging/prod)
* Redis integration
* Logging + monitoring
* CI/CD pipeline
* Structured migrations strategy
* Permission system standardization

---

# 3. What You Are Doing (Phase-Oriented View)

## Phase 0 — Setup (Partial)

* Environment
* Git
* Base Django project

## Phase 1 — Foundation Layer (ONGOING)

* Core architecture primitives
* Identity system
* Base module pattern
* Docker stabilization

## Phase 2 — Core System Layer (NEXT)

* Permissions & roles
* Shared utilities
* API base framework
* Admin system (WowDash integration)

---

# 4. Target State After Phase 2

After Phase 2, you should have:

* Stable Docker-based environment
* Fully working custom user system
* Reusable module blueprint
* API structure standardized
* Role/permission system ready
* Admin dashboard integrated
* Base services layer enforced

---

# 5. Execution Prompts (DeepSeek-Optimized)

These are **production prompts**. Use them exactly as-is.

---

# 🔹 MASTER CONTEXT (USE IN EVERY PROMPT)

```text id="ctx-juxtgo"
You are a senior Django backend engineer working inside JuxtGo OS.

System Context:
- Modular Django architecture
- PostgreSQL database
- Redis (planned)
- Dockerized environment
- Nginx reverse proxy
- Feature-based modular apps

Architecture Rules:
- Strict separation of concerns
- No business logic in views
- Use service layer pattern
- Modular and reusable apps only
- Production-ready code only

Output Format:
1. Technical plan
2. Code
3. Tradeoffs / risks
```

---

# 🔹 PHASE 1 PROMPTS (FOUNDATION)

---

## 1. Fix Docker + PostgreSQL Setup

```text id="p1-docker"
[ctx-juxtgo]

Task:
Fix and standardize Docker setup for Django + PostgreSQL.

Requirements:
- Multi-container Docker Compose
- Services: web, db, redis (optional placeholder)
- Proper environment variables
- Persistent DB volume
- Hot reload for development

Output:
1. docker-compose.yml
2. Dockerfile
3. .env structure
4. Setup instructions
5. Debug checklist for common issues
```

---

## 2. Base Django Project Structure

```text id="p1-structure"
[ctx-juxtgo]

Task:
Define production-grade folder structure for JuxtGo OS.

Requirements:
- apps/core/
- apps/shared/
- apps/features/
- config/settings split (base/dev/prod)
- clear separation of layers

Output:
1. Folder tree
2. Explanation of each layer
3. Best practices for scaling
```

---

## 3. Identity Module (Custom User)

```text id="p1-identity"
[ctx-juxtgo]

Task:
Implement identity module with custom user model.

Requirements:
- Email-based authentication
- AbstractBaseUser
- Manager class
- Admin integration
- Migration-safe design

Output:
1. Models
2. Managers
3. Admin config
4. Migration strategy
```

---

## 4. Base Module Template (CRITICAL)

```text id="p1-template"
[ctx-juxtgo]

Task:
Create a reusable Django module template.

Requirements:
- models/
- services/
- api/
- selectors/
- permissions/
- tests/

Include:
- example CRUD
- service layer usage
- serializer structure

Output:
1. Full module template
2. Example implementation
3. Usage guide
```

---

# 🔹 PHASE 2 PROMPTS (CORE SYSTEM)

---

## 5. Role & Permission System

```text id="p2-permissions"
[ctx-juxtgo]

Task:
Design and implement a scalable role and permission system.

Requirements:
- Role-based access control (RBAC)
- Extend Django permissions or custom system
- Assign roles to users
- API-level enforcement

Output:
1. Data model
2. Services
3. Permission classes
4. Example usage
```

---

## 6. Shared Utilities Layer

```text id="p2-shared"
[ctx-juxtgo]

Task:
Create shared utilities module.

Include:
- base models (timestamps, soft delete)
- response format standardization
- exception handling
- logging utilities

Output:
1. Code
2. Usage patterns
```

---

## 7. API Base Framework

```text id="p2-api"
[ctx-juxtgo]

Task:
Standardize API layer across JuxtGo OS.

Requirements:
- BaseAPIView / BaseViewSet
- Unified response format
- Error handling middleware
- Pagination standard

Output:
1. Base classes
2. Example usage
3. Integration guide
```

---

## 8. WowDash Admin Integration

```text id="p2-wowdash"
[ctx-juxtgo]

Task:
Integrate WowDash admin template into Django admin.

Requirements:
- Custom admin UI
- Static files setup
- Template overrides
- Clean integration (no hacks)

Output:
1. Setup steps
2. Config changes
3. Example admin page
```

---

# 6. Execution Discipline (Non-Negotiable)

When using DeepSeek:

* One prompt = one task
* Never mix phases
* Always review output before implementation
* Validate with GPT/Claude if critical

---

# 7. Immediate Next Step

You should now:

1. Run → **Docker Fix Prompt**
2. Then → **Structure Prompt**
3. Then → **Identity Module**
4. Then → **Module Template**

Do NOT jump to Phase 2 until Phase 1 is stable.

---

If you want, next I can:

* audit your current repo structure
* fix your Docker error live
* or generate the exact production-ready code for Phase 1

Just specify the target.
