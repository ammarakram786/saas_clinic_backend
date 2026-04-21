from django_filters import rest_framework as filters

from control.models import PlatformAuditLog


class PlatformAuditLogFilter(filters.FilterSet):
    actor = filters.UUIDFilter(field_name='actor_id')
    tenant = filters.UUIDFilter(field_name='tenant_id')
    action = filters.CharFilter(field_name='action', lookup_expr='iexact')
    resource_type = filters.CharFilter(field_name='resource_type', lookup_expr='iexact')
    resource_id = filters.CharFilter(field_name='resource_id', lookup_expr='iexact')
    since = filters.DateTimeFilter(field_name='created_at', lookup_expr='gte')
    until = filters.DateTimeFilter(field_name='created_at', lookup_expr='lte')

    class Meta:
        model = PlatformAuditLog
        fields = ('actor', 'tenant', 'action', 'resource_type', 'resource_id')
