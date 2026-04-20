from django_filters import rest_framework as filters
from django.db.models import Q

from platform_ctrl.models import Tenant


class TenantFilter(filters.FilterSet):
    status = filters.CharFilter(field_name='status', lookup_expr='iexact')
    country = filters.CharFilter(field_name='country', lookup_expr='iexact')
    onboarded_after = filters.DateTimeFilter(field_name='onboarded_at', lookup_expr='gte')
    onboarded_before = filters.DateTimeFilter(field_name='onboarded_at', lookup_expr='lte')
    search = filters.CharFilter(method='filter_search')

    class Meta:
        model = Tenant
        fields = ('status', 'country')

    def filter_search(self, queryset, name, value):
        if not value:
            return queryset
        return queryset.filter(
            Q(name__icontains=value)
            | Q(slug__icontains=value)
            | Q(contact_email__icontains=value)
        )
