import django_filters as filters
from account.models import User

class UserFilter(filters.FilterSet):
    name = filters.CharFilter(field_name='name', lookup_expr='contains')
    username = filters.CharFilter(field_name='username', lookup_expr='contains')
    role = filters.CharFilter(field_name='role__code_name', lookup_expr='exact')
    exclude_user = filters.NumberFilter(field_name='id', exclude=True)
    status = filters.CharFilter(field_name='status', lookup_expr='exact')
    
    
    email = filters.CharFilter(field_name='email', lookup_expr='contains')


    class Meta:
        model = User
        fields = ['name', 'username', 'role', 'exclude_user', 'status', 'email']
