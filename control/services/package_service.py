from django.db import transaction

from control.models import Feature, Package, PackageFeature


@transaction.atomic
def create_package(*, data: dict, features: list | None = None, actor=None) -> Package:
    package = Package.objects.create(**data)
    if features:
        _apply_features(package, features)
        _recompute_tenants_on_package(package)
    return package


@transaction.atomic
def update_package(*, package: Package, data: dict, actor=None) -> Package:
    for field, value in data.items():
        setattr(package, field, value)
    package.save()
    return package


@transaction.atomic
def set_package_features(*, package: Package, features: list, actor=None) -> Package:
    """Replace the package's feature set transactionally."""
    PackageFeature.objects.filter(package=package).delete()
    _apply_features(package, features)
    package.save(update_fields=['updated_at'])
    _recompute_tenants_on_package(package)
    return package


def _apply_features(package: Package, features: list):
    """
    ``features`` is a list of dicts ``{feature|feature_id, limit_value}``.
    """
    rows = []
    for row in features:
        feature = row.get('feature') or row.get('feature_id')
        if not isinstance(feature, Feature):
            feature = Feature.objects.get(pk=feature)
        rows.append(PackageFeature(
            package=package,
            feature=feature,
            limit_value=row.get('limit_value'),
        ))
    PackageFeature.objects.bulk_create(rows)


def _recompute_tenants_on_package(package: Package):
    from control.models import Tenant
    from control.services.entitlements import recompute_entitlements

    tenants = Tenant.objects.filter(
        subscriptions__package=package,
    ).distinct()

    def _do():
        for t in tenants:
            recompute_entitlements(t)

    transaction.on_commit(_do)
