from control.filters import SubscriptionFilter
from control.models import TenantSubscription
from control.serializers import SubscriptionSerializer
from control.views.platform_base import PlatformReadOnlyViewSet


class SubscriptionViewSet(PlatformReadOnlyViewSet):
    queryset = (
        TenantSubscription.objects
        .select_related('tenant', 'package')
        .order_by('-created_at')
    )
    serializer_class = SubscriptionSerializer
    filterset_class = SubscriptionFilter
    search_fields = ('tenant__name', 'tenant__slug', 'package__code')
    ordering_fields = ('created_at', 'starts_at', 'ends_at', 'status')

    permissions_map = {
        'list':     ['platform.subscription.read'],
        'retrieve': ['platform.subscription.read'],
    }
