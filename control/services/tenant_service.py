"""
Tenant lifecycle services.

All public callables are ``transaction.atomic`` and take an ``actor`` (a
``PlatformUser``) so audit logging has an attributable actor. The actor is
recorded in ``PlatformAuditLog`` (via signals + audit context), NOT in
``BaseMixin.created_by/updated_by`` - those FKs target ``account.User``
and can't reference a platform user.

Each mutation schedules ``recompute_entitlements`` on commit so the
Redis-backed entitlement snapshot stays in sync.
"""

from django.db import transaction
from django.utils import timezone

from control.models import Tenant
from control.models.tenant import TenantStatus
from control.services.entitlements import schedule_recompute


@transaction.atomic
def create_tenant(*, data: dict, actor=None) -> Tenant:
    tenant = Tenant.objects.create(**data)
    schedule_recompute(tenant)
    return tenant


@transaction.atomic
def update_tenant(*, tenant: Tenant, data: dict, actor=None) -> Tenant:
    for field, value in data.items():
        setattr(tenant, field, value)
    tenant.save()
    schedule_recompute(tenant)
    return tenant


@transaction.atomic
def suspend_tenant(*, tenant: Tenant, reason: str = '', actor=None) -> Tenant:
    tenant.status = TenantStatus.SUSPENDED
    tenant.suspended_at = timezone.now()
    tenant.suspended_reason = reason or ''
    tenant.save(update_fields=[
        'status', 'suspended_at', 'suspended_reason', 'updated_at',
    ])
    schedule_recompute(tenant)
    return tenant


@transaction.atomic
def activate_tenant(*, tenant: Tenant, actor=None) -> Tenant:
    tenant.status = TenantStatus.ACTIVE
    tenant.suspended_at = None
    tenant.suspended_reason = None
    if tenant.onboarded_at is None:
        tenant.onboarded_at = timezone.now()
    tenant.save(update_fields=[
        'status', 'suspended_at', 'suspended_reason',
        'onboarded_at', 'updated_at',
    ])
    schedule_recompute(tenant)
    return tenant


@transaction.atomic
def cancel_tenant(*, tenant: Tenant, actor=None) -> Tenant:
    tenant.status = TenantStatus.CANCELLED
    tenant.cancelled_at = timezone.now()
    tenant.save(update_fields=['status', 'cancelled_at', 'updated_at'])
    schedule_recompute(tenant)
    return tenant
