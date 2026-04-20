from django.core.cache import cache
from django.db.models import Count, Q
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from platform_ctrl.models import Tenant, TenantFeatureOverride, TenantSubscription
from platform_ctrl.models.subscription import ACTIVE_STATUSES
from platform_ctrl.models.tenant import TenantStatus
from platform_ctrl.permissions import IsPlatformStaff
from util.permissions import DynamicRolePermission


CACHE_KEY = 'platform:stats:v1'
CACHE_TIMEOUT = 60


class PlatformStatsView(APIView):
    permission_classes = (IsAuthenticated, IsPlatformStaff, DynamicRolePermission)
    action = 'stats'
    permissions_map = {
        'stats': ['platform.audit.read'],
    }

    def get(self, request):
        hit = cache.get(CACHE_KEY)
        if hit is not None:
            return Response(hit)

        data = _compute_stats()
        cache.set(CACHE_KEY, data, timeout=CACHE_TIMEOUT)
        return Response(data)


def _compute_stats():
    tenant_counts = Tenant.objects.aggregate(
        total=Count('id'),
        active=Count('id', filter=Q(status=TenantStatus.ACTIVE)),
        trial=Count('id', filter=Q(status=TenantStatus.TRIAL)),
        suspended=Count('id', filter=Q(status=TenantStatus.SUSPENDED)),
        cancelled=Count('id', filter=Q(status=TenantStatus.CANCELLED)),
    )

    sub_by_pkg = (
        TenantSubscription.objects
        .filter(status__in=[s.value for s in ACTIVE_STATUSES])
        .values('package__code')
        .annotate(count=Count('id'))
        .order_by('package__code')
    )

    enabled_by_feature: dict[str, int] = {}
    for tenant in Tenant.objects.only('limits_snapshot'):
        for code, row in (tenant.limits_snapshot or {}).items():
            if isinstance(row, dict) and row.get('enabled'):
                enabled_by_feature[code] = enabled_by_feature.get(code, 0) + 1

    overrides = TenantFeatureOverride.objects.count()

    return {
        'tenants': tenant_counts,
        'subscriptions': {
            'active_by_package': {r['package__code']: r['count'] for r in sub_by_pkg},
        },
        'features': {
            'enabled_by_feature': enabled_by_feature,
        },
        'overrides': {
            'total': overrides,
        },
    }
