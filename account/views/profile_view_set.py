from account.models import Profile
from control.context import get_current_tenant
from rest_framework.exceptions import ValidationError
from account.serializers import ProfileSerializer
from .base_view import BaseAuditViewSet


class ProfileViewSet(BaseAuditViewSet):
    queryset = Profile.objects.all().order_by('-id')
    filterset_fields = ('user',)

    permissions_map = {
        'list': ['read_profile'],
        'retrieve': ['read_profile'],
        'create': ['create_profile'],
        'update': ['update_profile'],
        'partial_update': ['update_profile'],
        'destroy': ['delete_profile'],
    }

    def get_queryset(self):
        tenant = get_current_tenant()
        qs = super().get_queryset().select_related(
            'created_by', 'updated_by'
        )
        if tenant is None:
            return qs.none()
        return qs.filter(
            user__tenant_memberships__tenant=tenant,
            user__tenant_memberships__is_active=True,
        ).distinct()

    def get_serializer_class(self):
        return ProfileSerializer

    def _ensure_user_in_tenant(self, user):
        tenant = get_current_tenant()
        if tenant is None:
            raise ValidationError({'detail': 'Tenant context is required.'})
        in_tenant = user.tenant_memberships.filter(
            tenant=tenant,
            is_active=True,
        ).exists()
        if not in_tenant:
            raise ValidationError({'user': 'Selected user is not in the current tenant.'})

    def perform_create(self, serializer):
        user = serializer.validated_data.get('user')
        if user is None:
            raise ValidationError({'user': 'This field is required.'})
        self._ensure_user_in_tenant(user)
        super().perform_create(serializer)

    def perform_update(self, serializer):
        user = serializer.validated_data.get('user', serializer.instance.user)
        self._ensure_user_in_tenant(user)
        super().perform_update(serializer)


