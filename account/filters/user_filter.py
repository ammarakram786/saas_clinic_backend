import django_filters as filters
from account.models import User

class UserFilter(filters.FilterSet):
    username = filters.CharFilter(field_name='username', lookup_expr='icontains')
    role = filters.CharFilter(field_name='role__code_name', lookup_expr='exact')
    exclude_user = filters.NumberFilter(field_name='id', exclude=True)
    email = filters.CharFilter(field_name='email', lookup_expr='icontains')


    class Meta:
        model = User
        fields = ['username', 'role', 'exclude_user', 'email']
