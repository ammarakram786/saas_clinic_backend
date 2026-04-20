from account.filters import RoleFilter
from account.models import Role
from account.serializers import RoleSerializer
from .base_view import BaseAuditViewSet


class RoleViewSet(BaseAuditViewSet):
    queryset = Role.objects.exclude(code_name='su').order_by('-id')
    filterset_class = RoleFilter

    permissions_map = {
        'list': ['read_role'],
        'retrieve': ['read_role'],
        'create': ['create_role'],
        'update': ['update_role'],
        'partial_update': ['update_role'],
        'destroy': ['delete_role'],
    }

    def get_queryset(self):
        return super().get_queryset().select_related(
            'created_by', 'updated_by'
        ).prefetch_related('permissions')

    def get_serializer_class(self):
        return RoleSerializer


