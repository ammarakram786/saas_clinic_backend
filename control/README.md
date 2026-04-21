# Control Plane Runbook

`control` is the platform-operator API surface (`/api/platform/*`).

## Bootstrapping

1. `python manage.py migrate`
2. `python manage.py seed_platform_rbac`
3. `python manage.py bootstrap_platform`
4. `python manage.py seed_features`
5. `python manage.py seed_packages`

For local sqlite testing:

- PowerShell: `$env:SQLITE_PATH='db.sqlite3'`

## First login

- Endpoint: `POST /api/platform/auth/login/`
- Body: `{ "email": "...", "password": "..." }`
- Cookies: `platform_access`, `platform_refresh`

## Core operator flows

- Manage operators: `/api/platform/platform-users/`
- Manage operator roles: `/api/platform/platform-roles/`
- Manage permissions catalog: `/api/platform/platform-permissions/`
  - Built-in permissions are read-only.
  - Custom permissions are writable and preserved by reseeding.
- Onboard tenant: `POST /api/platform/tenants/`
- Assign package: `POST /api/platform/tenants/{id}/assign-package/`
- Feature override: `POST /api/platform/tenants/{id}/overrides/`
- Audit: `GET /api/platform/audit-logs/`
- Stats: `GET /api/platform/stats/`

## RBAC notes

- Enforcement uses `DynamicRolePermission` + per-view `permissions_map`.
- Runtime role<->permission assignment is dynamic.
- Action->permission mapping remains code-owned to prevent accidental lockout.
