from django.db import transaction
from django.utils import timezone

from platform_ctrl.models import Package, PackageFeature, TenantSubscription
from platform_ctrl.models.subscription import (
    BillingCycle,
    SubscriptionStatus,
    ACTIVE_STATUSES,
)
from platform_ctrl.services.entitlements import schedule_recompute


def _snapshot_features_for(package: Package) -> dict:
    rows = PackageFeature.objects.filter(
        package=package, feature__is_active=True,
    ).select_related('feature')
    return {row.feature.code: row.limit_value for row in rows}


@transaction.atomic
def assign_package(
    *,
    tenant,
    package_id=None,
    package: Package | None = None,
    billing_cycle: str = BillingCycle.MONTHLY,
    starts_at=None,
    ends_at=None,
    auto_renew: bool = True,
    actor=None,
) -> TenantSubscription:
    """
    Replace the tenant's active subscription.

    Cancels any existing TRIAL/ACTIVE sub, creates a new one with a frozen
    ``feature_snapshot``, and schedules entitlement recomputation on commit.
    """
    if package is None:
        if package_id is None:
            raise ValueError('package or package_id required')
        package = Package.objects.get(pk=package_id)

    active = TenantSubscription.objects.select_for_update().filter(
        tenant=tenant, status__in=[s.value for s in ACTIVE_STATUSES],
    )
    for sub in active:
        sub.status = SubscriptionStatus.CANCELLED
        sub.ends_at = timezone.now()
        sub.updated_by = actor
        sub.save(update_fields=['status', 'ends_at', 'updated_by', 'updated_at'])

    sub = TenantSubscription.objects.create(
        tenant=tenant,
        package=package,
        billing_cycle=billing_cycle,
        status=SubscriptionStatus.ACTIVE,
        starts_at=starts_at or timezone.now(),
        ends_at=ends_at,
        auto_renew=auto_renew,
        feature_snapshot=_snapshot_features_for(package),
        created_by=actor,
        updated_by=actor,
    )
    schedule_recompute(tenant)
    return sub


@transaction.atomic
def cancel_subscription(*, subscription: TenantSubscription, actor=None) -> TenantSubscription:
    subscription.status = SubscriptionStatus.CANCELLED
    subscription.ends_at = timezone.now()
    subscription.updated_by = actor
    subscription.save(update_fields=['status', 'ends_at', 'updated_by', 'updated_at'])
    schedule_recompute(subscription.tenant)
    return subscription


@transaction.atomic
def renew_subscription(*, subscription: TenantSubscription, new_ends_at=None, actor=None) -> TenantSubscription:
    subscription.status = SubscriptionStatus.ACTIVE
    if new_ends_at is not None:
        subscription.ends_at = new_ends_at
    subscription.updated_by = actor
    subscription.save(update_fields=['status', 'ends_at', 'updated_by', 'updated_at'])
    schedule_recompute(subscription.tenant)
    return subscription
