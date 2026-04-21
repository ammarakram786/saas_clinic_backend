from rest_framework import status
from rest_framework.decorators import action
from rest_framework.exceptions import ValidationError
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from control.context import get_current_tenant
from account.models import User, Role, TenantMembership
from account.serializers import UserSerializer, ChangePasswordSerializer
from account.filters import UserFilter
from .base_view import BaseAuditViewSet


class UserViewSet(BaseAuditViewSet):
    queryset = User.objects.all().order_by('-id')
    serializer_class = UserSerializer
    filterset_class = UserFilter

    permissions_map = {
        'list': ['read_user'],
        'retrieve': ['read_user'],
        'create': ['create_user'],
        'update': ['update_user'],
        'partial_update': ['update_user'],
        'destroy': ['delete_user'],
    }

    def get_queryset(self):
        tenant = get_current_tenant()
        qs = super().get_queryset()
        if tenant is None:
            return qs.none()
        return qs.filter(
            tenant_memberships__tenant=tenant,
            tenant_memberships__is_active=True,
        ).distinct()

    def get_serializer_class(self):
        return UserSerializer

    def perform_create(self, serializer):
        tenant = get_current_tenant()
        if tenant is None:
            raise ValidationError({'detail': 'Tenant context is required.'})

        user = serializer.save()
        role_id = self.request.data.get('membership_role')
        role = None
        if role_id:
            role = Role.objects.filter(pk=role_id).first()

        TenantMembership.objects.update_or_create(
            user=user,
            tenant=tenant,
            defaults={
                'role': role,
                'is_active': True,
                'invited_by': self.request.user,
                'updated_by': self.request.user,
            },
        )
        self._log_action(user, 'CREATE')

    def perform_update(self, serializer):
        user = serializer.save()
        tenant = get_current_tenant()
        role_id = self.request.data.get('membership_role')
        if tenant is not None and role_id:
            role = Role.objects.filter(pk=role_id).first()
            TenantMembership.objects.filter(
                user=user,
                tenant=tenant,
                is_active=True,
            ).update(role=role)
        self._log_action(user, 'UPDATE')

    def perform_destroy(self, instance):
        tenant = get_current_tenant()
        if tenant is None:
            return
        self._log_action(instance, 'DELETE')
        TenantMembership.objects.filter(
            user=instance,
            tenant=tenant,
        ).update(is_active=False)

    @action(detail=False, methods=['post'], url_path='change-password', url_name='change_password', permission_classes=[IsAuthenticated])
    def change_password(self, request):
        serializer = ChangePasswordSerializer(data=request.data, context={'request': request})
        if serializer.is_valid():
            user = request.user
            user.set_password(serializer.validated_data['new_password'])
            user.initial_reset = True
            user.save()
            return Response({"detail": "Password has been changed successfully."}, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


    
