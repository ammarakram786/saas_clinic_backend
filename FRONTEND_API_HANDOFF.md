# Frontend API Handoff

This document summarizes the implemented backend APIs, auth rules, and integration constraints for parallel frontend development.

## Scope

Two access layers are active:

1. Platform Operators (Owner layer) via `/api/platform/*`
2. Tenant Staff (Clinic layer) via `/api/account/*`

## Global Integration Rules

- Use cookie auth with `withCredentials: true` on frontend requests.
- Keep platform and tenant sessions fully separated.
- Gate UI actions by backend `permissions[]`.
- Treat cross-tenant resource access as denied/not-found.
- Do not allow editing/deleting built-in platform permissions (`is_builtin=true`).

## Auth Planes

### Platform auth

Base: `/api/platform/auth/`

- `POST login/`
- `POST refresh/`
- `POST logout/`
- `GET me/`

Cookies:

- `platform_access`
- `platform_refresh`

### Tenant auth

Base: `/api/account/auth/`

- `POST login/`
- `POST refresh/`
- `POST logout/`
- `GET me/`

Cookies:

- `access_token`
- `refresh_token`

Tenant login payload:

```json
{
  "username": "clinic_admin_1",
  "password": "******",
  "tenant_slug": "clinic-a"
}
```

Tenant `login` and `me` responses include:

- `tenant: { id, name, slug }`
- `membership_id`
- `permissions: string[]`

## Platform APIs (`/api/platform/`)

- `tenants/` (CRUD)
- `tenants/{id}/suspend/` (POST)
- `tenants/{id}/activate/` (POST)
- `tenants/{id}/cancel/` (POST)
- `tenants/{id}/features/` (GET)
- `tenants/{id}/assign-package/` (POST)
- `tenants/{id}/overrides/` (GET, POST)
- `tenants/{id}/overrides/{feature_code}/` (PATCH, DELETE)
- `features/` (CRUD)
- `packages/` (CRUD)
- `subscriptions/` (read/list)
- `platform-users/` (CRUD)
- `platform-users/{id}/set-password/` (POST)
- `platform-users/{id}/activate/` (POST)
- `platform-users/{id}/deactivate/` (POST)
- `platform-roles/` (CRUD)
- `platform-permissions/` (CRUD, built-in rows protected)
- `audit-logs/` (GET/list)
- `stats/` (GET)

## Tenant APIs (`/api/account/`)

- `users/` (tenant-scoped CRUD behavior)
- `users-list/` (tenant-scoped lightweight list)
- `roles/` (tenant role management)
- `profiles/` (tenant-scoped CRUD)
- `permissions/` (tenant permission catalog list)

## Dynamic Permission Catalog (Platform)

`/api/platform/platform-permissions/` model shape:

```json
{
  "id": 1,
  "code_name": "platform.tenant.read",
  "name": "Read Tenants",
  "module": "tenant",
  "description": "View tenant list and details.",
  "is_builtin": true
}
```

Rules:

- Built-in permissions are read-only.
- Built-in delete returns HTTP `409`.
- Custom permissions are writable and preserved during RBAC reseeding.

## Frontend Guarding Rules

### Platform app

- Require successful `/api/platform/auth/me/`.
- Gate per action using returned permissions.

### Tenant app

- Require successful `/api/account/auth/me/`.
- Require active tenant context (`user.tenant`).
- Gate per action using membership permissions.

## Suggested frontend types

```ts
type TenantContext = {
  id: string;
  name: string;
  slug: string;
};

type CurrentUser = {
  id: string | number;
  username?: string;
  email?: string;
  tenant?: TenantContext;
  membership_id?: number;
  permissions: string[];
};

type PlatformPermission = {
  id: number;
  code_name: string;
  name: string;
  module: string;
  description: string;
  is_builtin: boolean;
};
```

## Recommended parallel frontend work

### Operator frontend

- Auth/session bootstrap
- Tenant lifecycle screens
- Feature/package/subscription assignment flows
- Platform users/roles/permissions screens
- Audit and stats dashboards

### Tenant frontend

- Login with `tenant_slug`
- `me`-driven app shell
- Tenant-scoped users/profiles management
- Role-permission gated components/actions
