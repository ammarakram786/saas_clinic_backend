from django.shortcuts import get_object_or_404
from django.contrib.auth.password_validation import validate_password
from rest_framework import serializers, status
from rest_framework.response import Response
from rest_framework.decorators import action

from control.models import PlatformPermission, PlatformRole, PlatformUser
from control.serializers import (
    PlatformPermissionSerializer,
    PlatformRoleSerializer,
    PlatformUserSerializer,
    PlatformUserCreateSerializer,
)
from control.views.platform_base import PlatformViewSet


class PlatformUserViewSet(PlatformViewSet):
    queryset = PlatformUser.objects.all().select_related('role').order_by('email')
    serializer_class = PlatformUserSerializer
    search_fields = ('email', 'full_name')
    ordering_fields = ('email', 'full_name', 'created_at', 'is_active')
    filterset_fields = ('is_active', 'role')

    permissions_map = {
        'list':           ['platform.platform_user.read'],
        'retrieve':       ['platform.platform_user.read'],
        'create':         ['platform.platform_user.manage'],
        'update':         ['platform.platform_user.manage'],
        'partial_update': ['platform.platform_user.manage'],
        'destroy':        ['platform.platform_user.manage'],
        'set_password':   ['platform.platform_user.manage'],
        'activate':       ['platform.platform_user.manage'],
        'deactivate':     ['platform.platform_user.manage'],
    }

    def get_serializer_class(self):
        if self.action == 'create':
            return PlatformUserCreateSerializer
        return PlatformUserSerializer

    def perform_create(self, serializer):
        serializer.save()

    @action(detail=True, methods=['post'], url_path='set-password')
    def set_password(self, request, pk=None):
        user = self.get_object()

        class _SetPasswordSerializer(serializers.Serializer):
            password = serializers.CharField(write_only=True, validators=[validate_password])

        payload = _SetPasswordSerializer(data=request.data)
        payload.is_valid(raise_exception=True)
        user.set_password(payload.validated_data['password'])
        user.save(update_fields=['password'])
        return Response({'msg': 'Password updated successfully.'}, status=status.HTTP_200_OK)

    @action(detail=True, methods=['post'])
    def activate(self, request, pk=None):
        user = self.get_object()
        if not user.is_active:
            user.is_active = True
            user.save(update_fields=['is_active'])
        return Response({'msg': 'Platform user activated.'}, status=status.HTTP_200_OK)

    @action(detail=True, methods=['post'])
    def deactivate(self, request, pk=None):
        user = self.get_object()
        if user.is_active:
            user.is_active = False
            user.save(update_fields=['is_active'])
        return Response({'msg': 'Platform user deactivated.'}, status=status.HTTP_200_OK)


class PlatformRoleViewSet(PlatformViewSet):
    queryset = PlatformRole.objects.all().prefetch_related('permissions').order_by('name')
    serializer_class = PlatformRoleSerializer
    search_fields = ('name', 'code_name')
    ordering_fields = ('name', 'code_name')

    permissions_map = {
        'list':           ['platform.platform_role.read'],
        'retrieve':       ['platform.platform_role.read'],
        'create':         ['platform.platform_role.manage'],
        'update':         ['platform.platform_role.manage'],
        'partial_update': ['platform.platform_role.manage'],
        'destroy':        ['platform.platform_role.manage'],
    }


class PlatformPermissionViewSet(PlatformViewSet):
    queryset = PlatformPermission.objects.all().order_by('module', 'code_name')
    serializer_class = PlatformPermissionSerializer
    search_fields = ('name', 'code_name', 'module')
    ordering_fields = ('module', 'code_name', 'name', 'is_builtin')
    filterset_fields = ('module', 'is_builtin')

    permissions_map = {
        'list':           ['platform.platform_permission.read'],
        'retrieve':       ['platform.platform_permission.read'],
        'create':         ['platform.platform_permission.manage'],
        'update':         ['platform.platform_permission.manage'],
        'partial_update': ['platform.platform_permission.manage'],
        'destroy':        ['platform.platform_permission.manage'],
    }

    def _get_writable_obj(self):
        obj = get_object_or_404(self.get_queryset(), pk=self.kwargs.get('pk'))
        if obj.is_builtin:
            raise serializers.ValidationError(
                {'detail': 'Built-in permissions are read-only.'}
            )
        return obj

    def update(self, request, *args, **kwargs):
        self._get_writable_obj()
        return super().update(request, *args, **kwargs)

    def partial_update(self, request, *args, **kwargs):
        self._get_writable_obj()
        return super().partial_update(request, *args, **kwargs)

    def destroy(self, request, *args, **kwargs):
        obj = self.get_object()
        if obj.is_builtin:
            return Response(
                {'detail': 'Built-in permissions cannot be deleted.'},
                status=status.HTTP_409_CONFLICT,
            )
        return super().destroy(request, *args, **kwargs)
