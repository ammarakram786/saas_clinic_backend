# Tenant Staff Runbook

`account` is the tenant-staff API surface (`/api/account/*`).

## Tenancy model

- Tenant users are `account.User`.
- Tenant affiliation is via `account.TenantMembership`:
  - `user` -> `account.User`
  - `tenant` -> `control.Tenant`
  - `role` -> `account.Role`
- Membership role is authoritative for tenant-plane authorization.

## RBAC bootstrap

Run:

- `python manage.py seed_account_rbac`

This seeds:

- Permission catalog (`read_user`, `create_user`, etc.)
- Baseline roles (`clinic_admin`, `clinic_staff`, `clinic_read_only`)

## Login and context

- Endpoint: `POST /api/account/auth/login/`
- Body: `{ "username": "...", "password": "...", "tenant_slug": "..." }`
- Tokens include `tenant_id`/`membership_id` claims.
- Middleware resolves tenant context from those claims and active membership.

## Tenant staff flows

- Current user: `GET /api/account/auth/me/`
- Users (tenant-scoped): `/api/account/users/`
- Profiles (tenant-scoped): `/api/account/profiles/`
- Roles/permissions: `/api/account/roles/`, `/api/account/permissions/`

Cross-tenant object access is denied by queryset scoping.
