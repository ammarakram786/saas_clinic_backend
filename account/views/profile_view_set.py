from account.filters import RoleFilter
from account.models import Profile
from account.serializers import ProfileSerializer
from .base_view import BaseAuditViewSet


class ProfileViewSet(BaseAuditViewSet):
    queryset = Profile.objects.exclude(code_name='su').order_by('-id')
    filterset_class = RoleFilter

    permissions_map = {
        'list': ['read_profile'],
        'retrieve': ['read_profile'],
        'create': ['create_profile'],
        'update': ['update_profile'],
        'partial_update': ['update_profile'],
        'destroy': ['delete_profile'],
    }

    def get_queryset(self):
        return super().get_queryset().select_related(
            'created_by', 'updated_by'
        )

    def get_serializer_class(self):
        return ProfileSerializer


