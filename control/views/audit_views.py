from control.filters import PlatformAuditLogFilter
from control.models import PlatformAuditLog
from control.serializers import PlatformAuditLogSerializer
from control.views.platform_base import PlatformReadOnlyViewSet


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
