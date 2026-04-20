from platform_ctrl.filters import PlatformAuditLogFilter
from platform_ctrl.models import PlatformAuditLog
from platform_ctrl.serializers import PlatformAuditLogSerializer
from platform_ctrl.views.platform_base import PlatformReadOnlyViewSet


class PlatformAuditLogViewSet(PlatformReadOnlyViewSet):
    queryset = (
        PlatformAuditLog.objects
        .select_related('actor', 'tenant')
        .order_by('-created_at')
    )
    serializer_class = PlatformAuditLogSerializer
    filterset_class = PlatformAuditLogFilter
    search_fields = ('resource_type', 'resource_id', 'request_id')
    ordering_fields = ('created_at', 'action', 'resource_type')

    permissions_map = {
        'list':     ['platform.audit.read'],
        'retrieve': ['platform.audit.read'],
    }
