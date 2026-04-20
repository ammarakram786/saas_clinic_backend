import django_filters as filters
from account.models import Role


class RoleFilter(filters.FilterSet):
    name = filters.CharFilter(field_name='name', lookup_expr='icontains')
    code_name = filters.CharFilter(field_name='code_name')

    class Meta:
        model = Role
        fields = [
            'name',
            'code_name'
        ]
