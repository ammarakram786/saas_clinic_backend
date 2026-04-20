from django.db import transaction

from platform_ctrl.models import Feature


@transaction.atomic
def create_feature(*, data: dict, actor=None) -> Feature:
    return Feature.objects.create(created_by=actor, updated_by=actor, **data)


@transaction.atomic
def update_feature(*, feature: Feature, data: dict, actor=None) -> Feature:
    was_active = feature.is_active
    for field, value in data.items():
        setattr(feature, field, value)
    feature.updated_by = actor
    feature.save()

    if was_active != feature.is_active:
        _recompute_all_affected(feature)
    return feature


@transaction.atomic
def deactivate_feature(*, feature: Feature, actor=None) -> Feature:
    feature.is_active = False
    feature.updated_by = actor
    feature.save(update_fields=['is_active', 'updated_by', 'updated_at'])
    _recompute_all_affected(feature)
    return feature


def _recompute_all_affected(feature: Feature):
    """Recompute entitlements for every tenant whose active sub uses this feature."""
    from platform_ctrl.models import Tenant, PackageFeature
    from platform_ctrl.services.entitlements import recompute_entitlements

    package_ids = PackageFeature.objects.filter(
        feature=feature,
    ).values_list('package_id', flat=True)

    tenants = Tenant.objects.filter(
        subscriptions__package_id__in=list(package_ids),
    ).distinct()

    def _do():
        for t in tenants:
            recompute_entitlements(t)

    transaction.on_commit(_do)
