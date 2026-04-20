from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from platform_ctrl.models import PlatformPermission, PlatformRole, PlatformUser
from platform_ctrl.permissions import IsPlatformStaff
from platform_ctrl.serializers import (
    PlatformPermissionSerializer,
    PlatformRoleSerializer,
    PlatformUserSerializer,
    PlatformUserCreateSerializer,
)
from platform_ctrl.views.platform_base import PlatformViewSet


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
    }

    def get_serializer_class(self):
        if self.action == 'create':
            return PlatformUserCreateSerializer
        return PlatformUserSerializer

    def perform_create(self, serializer):
        serializer.save()


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


class PlatformPermissionListView(APIView):
    permission_classes = (IsAuthenticated, IsPlatformStaff)

    def get(self, request):
        qs = PlatformPermission.objects.all().order_by('module', 'code_name')
        return Response(PlatformPermissionSerializer(qs, many=True).data)
