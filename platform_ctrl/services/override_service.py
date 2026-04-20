from django.db import transaction

from platform_ctrl.models import Feature, TenantFeatureOverride
from platform_ctrl.services.entitlements import schedule_recompute


@transaction.atomic
def upsert_override(
    *,
    tenant,
    feature_code: str,
    is_enabled: bool = True,
    limit_value: int | None = None,
    expires_at=None,
    reason: str = '',
    actor=None,
) -> TenantFeatureOverride:
    feature = Feature.objects.get(code=feature_code)
    override, _ = TenantFeatureOverride.objects.update_or_create(
        tenant=tenant, feature=feature,
        defaults={
            'is_enabled': is_enabled,
            'limit_value': limit_value,
            'expires_at': expires_at,
            'reason': reason or '',
            'updated_by': actor,
        },
    )
    if override.created_by_id is None:
        override.created_by = actor
        override.save(update_fields=['created_by'])

    schedule_recompute(tenant)
    return override


@transaction.atomic
def remove_override(*, tenant, feature_code: str, actor=None):
    TenantFeatureOverride.objects.filter(
        tenant=tenant, feature__code=feature_code,
    ).delete()
    schedule_recompute(tenant)
