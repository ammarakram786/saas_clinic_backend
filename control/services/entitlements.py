"""
Effective-entitlements resolver for a tenant.

The resolver combines three inputs:

  1. the tenant's active subscription's ``feature_snapshot`` (frozen at
     subscription creation),
  2. any ``TenantFeatureOverride`` rows (can widen or narrow the package),
  3. the global ``Feature.is_active`` kill-switch (an inactive feature is
     forced off everywhere regardless of package / override).

The resolved map is persisted to ``Tenant.limits_snapshot`` and cached in
Redis. ``get_entitlements`` is the sole read path used by other code.
"""

from django.core.cache import cache
from django.db import transaction
from django.utils import timezone


CACHE_KEY = 'tenant:{pk}:features'
CACHE_TIMEOUT = None  # persist until invalidated


def _cache_key(tenant) -> str:
    return CACHE_KEY.format(pk=tenant.pk)


def compute_effective_features(tenant) -> dict:
    """
    Return ``{feature_code: {"enabled": bool, "limit": int|None, "source": "package"|"override"|"disabled"}}``.
    """
    from control.models import Feature, TenantFeatureOverride
    from control.models.subscription import ACTIVE_STATUSES

    active_feature_codes = set(
        Feature.objects.filter(is_active=True).values_list('code', flat=True)
    )

    effective: dict = {}

    sub = tenant.subscriptions.filter(status__in=[s.value for s in ACTIVE_STATUSES]).first()
    if sub is not None:
        for code, limit in (sub.feature_snapshot or {}).items():
            effective[code] = {
                'enabled': True,
                'limit': limit,
                'source': 'package',
            }

    now = timezone.now()
    for override in TenantFeatureOverride.objects.filter(tenant=tenant).select_related('feature'):
        if override.expires_at and override.expires_at <= now:
            continue
        code = override.feature.code
        effective[code] = {
            'enabled': bool(override.is_enabled),
            'limit': override.limit_value,
            'source': 'override',
        }

    for code, row in list(effective.items()):
        if code not in active_feature_codes:
            effective[code] = {
                'enabled': False,
                'limit': None,
                'source': 'disabled',
            }

    return effective


def recompute_entitlements(tenant) -> dict:
    """Recompute and persist. Safe to call inside or outside a transaction."""
    from control.models import Tenant

    data = compute_effective_features(tenant)
    Tenant.objects.filter(pk=tenant.pk).update(limits_snapshot=data)
    cache.set(_cache_key(tenant), data, timeout=CACHE_TIMEOUT)
    return data


def get_entitlements(tenant) -> dict:
    """
    Cheap read path: Redis -> ``Tenant.limits_snapshot`` -> compute.
    Returns the cached/snapshot dict.
    """
    hit = cache.get(_cache_key(tenant))
    if hit is not None:
        return hit

    if tenant.limits_snapshot:
        cache.set(_cache_key(tenant), tenant.limits_snapshot, timeout=CACHE_TIMEOUT)
        return tenant.limits_snapshot

    return recompute_entitlements(tenant)


def schedule_recompute(tenant):
    """
    Schedule ``recompute_entitlements`` to fire on transaction commit.
    Callers inside a transaction should prefer this over calling
    ``recompute_entitlements`` directly.
    """
    transaction.on_commit(lambda: recompute_entitlements(tenant))
