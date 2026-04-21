from django_filters import rest_framework as filters

from control.models import TenantSubscription


class SubscriptionFilter(filters.FilterSet):
    status = filters.CharFilter(field_name='status', lookup_expr='iexact')
    tenant = filters.UUIDFilter(field_name='tenant_id')
    package = filters.NumberFilter(field_name='package_id')
    billing_cycle = filters.CharFilter(field_name='billing_cycle', lookup_expr='iexact')

    class Meta:
        model = TenantSubscription
        fields = ('status', 'tenant', 'package', 'billing_cycle')
