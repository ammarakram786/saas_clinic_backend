# Agent / contributor notes — saas_clinic backend

This document is **project memory** for humans and coding agents: what the tree is for and where things live.

## Purpose

Multi-tenant SaaS backend for a clinic product: **tenant-facing** APIs (`account`) and **operator / platform** APIs (`control`) for tenants, billing packages, feature entitlements, platform staff, and audit.

## Stack (authoritative versions in `requirements.txt`)

- Django 6, DRF, drf-spectacular, django-filter, cors-headers, django-environ
- PostgreSQL, Redis, JWT (SimpleJWT + custom platform cookie/JWT in `control`)

## Layout

| Path | Role |
|------|------|
| `manage.py` | Django entrypoint |
| `backend/settings/` | `base.py` + env-specific (`dev.py`, `prod.py`) |
| `backend/urls.py` | Root URL routes |
| `account/` | Tenant users and account APIs (`/api/account/`) |
| `control/` | Control plane: tenants, subscriptions, features, packages, platform RBAC, audit (`/api/platform/`) |
| `util/` | Shared utilities |

## HTTP routes (high level)

- `/admin/` — Django admin (platform models registered in `control/admin.py`)
- `/api/account/` — account app
- `/api/platform/` — platform operator API
- `/api/schema/`, `/api/docs/` — OpenAPI + Swagger

## Conventions

- **`AUTH_USER_MODEL`**: `account.User` (tenant plane).
- **Platform staff** are **`PlatformUser`** instances; DRF permission **`IsPlatformStaff`** restricts platform views.
- **Tenant staff tenancy** is modeled via **`account.TenantMembership`** (`user` <-> `control.Tenant` with tenant-role per membership).
- **Tenant context** is set by middleware from tenant JWT claims (`tenant_id`) and membership checks.
- The Django app package is **`control`**, not `platform`, to avoid shadowing Python’s stdlib `platform` module.

## Local development (typical)

1. Copy / configure `.env` (see `django-environ` usage in `backend/settings/base.py`).
2. Ensure PostgreSQL and Redis match `DATABASE_URL` and `REDIS_URL`.
3. `python manage.py migrate` (when migrations exist), `python manage.py runserver`, optional `python manage.py createsuperuser` for `/admin/`.

## Management commands (bootstrap order)

Recommended order on a fresh environment:

1. `python manage.py migrate`
2. `python manage.py seed_platform_rbac`
3. `python manage.py bootstrap_platform` (set `PLATFORM_BOOTSTRAP_EMAIL` / `PLATFORM_BOOTSTRAP_PASSWORD`)
4. `python manage.py seed_account_rbac`
5. `python manage.py seed_features`
6. `python manage.py seed_packages`

Platform commands live in `control/management/commands/`; tenant RBAC seed is in `account/management/commands/`.

## Cursor rules

Project-wide AI rules live in **`.cursor/rules/*.mdc`** (see `saas-clinic-backend.mdc`). Add focused rules there for new persistent conventions instead of duplicating long prose here.
