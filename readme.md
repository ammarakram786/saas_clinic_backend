# SaaS Clinic Backend

Django 6 + DRF backend with a split "platform control plane" and (reserved) tenant plane.

## Quick start

```bash
python -m venv .venv
.venv\Scripts\activate          # Windows
# source .venv/bin/activate     # macOS / Linux
pip install -r requirements.txt
copy .env.example .env          # cp .env.example .env  on *nix
python manage.py migrate
python manage.py initialize_system
python manage.py runserver
```

## Settings

Settings live under `backend/settings/`:

- `base.py` - defaults, loaded everywhere.
- `dev.py` - local development (default `DJANGO_SETTINGS_MODULE`).
- `prod.py` - production hardening.

All env-driven values go through `django-environ`.

## Control plane

Mounted under `/api/platform/`:

- `auth/(login|logout|refresh|me)/`
- `tenants/`, `packages/`, `features/`, `subscriptions/`
- `platform-users/`, `platform-roles/`, `platform-permissions/`
- `audit-logs/`, `stats/`

Authenticated with `PlatformUser` + `platform_access` / `platform_refresh` cookies.
Authorized with per-action codenames (e.g. `platform.tenant.suspend`).

## Tenant plane

Reserved. `/api/account/*` stays mounted for the existing `account.User` but is
inert until the tenant plane work begins.
