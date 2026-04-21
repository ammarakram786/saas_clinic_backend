from rest_framework import status
from rest_framework.decorators import action
from rest_framework.response import Response

from control.filters import TenantFilter
from control.models import Tenant
from control.serializers import (
    TenantSerializer,
    TenantCreateSerializer,
)
from control.services import tenant_service
from control.services.entitlements import get_entitlements
from control.services.subscription_service import assign_package
from control.services.override_service import upsert_override, remove_override
from control.serializers.subscription import AssignPackageSerializer
from control.serializers.override import (
    TenantOverrideSerializer,
    TenantOverrideUpsertSerializer,
)
from control.models import TenantFeatureOverride
from control.views.platform_base import PlatformViewSet


class TenantViewSet(PlatformViewSet):
    queryset = Tenant.objects.all().order_by('-created_at')
    serializer_class = TenantSerializer
    filterset_class = TenantFilter
    search_fields = ('name', 'slug', 'contact_email')
    ordering_fields = ('name', 'slug', 'status', 'created_at', 'onboarded_at')
    lookup_field = 'pk'

    permissions_map = {
        'list':             ['platform.tenant.read'],
        'retrieve':         ['platform.tenant.read'],
        'create':           ['platform.tenant.create'],
        'update':           ['platform.tenant.update'],
        'partial_update':   ['platform.tenant.update'],
        'suspend':          ['platform.tenant.suspend'],
        'activate':         ['platform.tenant.activate'],
        'cancel':           ['platform.tenant.cancel'],
        'features':         ['platform.tenant.read'],
        'assign_package':   ['platform.subscription.assign'],
        'overrides':        ['platform.override.read', 'platform.override.manage'],
        'upsert_override':  ['platform.override.manage'],
        'delete_override':  ['platform.override.manage'],
        'mutate_override':  ['platform.override.manage'],
    }

    http_method_names = ['get', 'post', 'patch', 'put', 'head', 'options']

    def get_serializer_class(self):
        if self.action == 'create':
            return TenantCreateSerializer
        return TenantSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        tenant = tenant_service.create_tenant(
            data=serializer.validated_data, actor=request.user,
        )
        return Response(
            TenantSerializer(tenant, context={'request': request}).data,
            status=status.HTTP_201_CREATED,
        )

    def update(self, request, *args, **kwargs):
        tenant = self.get_object()
        partial = kwargs.pop('partial', False)
        serializer = TenantCreateSerializer(tenant, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        tenant = tenant_service.update_tenant(
            tenant=tenant, data=serializer.validated_data, actor=request.user,
        )
        return Response(TenantSerializer(tenant, context={'request': request}).data)

    # ─────────────────── Lifecycle actions ───────────────────
    @action(detail=True, methods=['post'])
    def suspend(self, request, pk=None):
        tenant = self.get_object()
        reason = request.data.get('reason', '') or ''
        tenant = tenant_service.suspend_tenant(
            tenant=tenant, reason=reason, actor=request.user,
        )
        return Response(TenantSerializer(tenant, context={'request': request}).data)

    @action(detail=True, methods=['post'])
    def activate(self, request, pk=None):
        tenant = self.get_object()
        tenant = tenant_service.activate_tenant(tenant=tenant, actor=request.user)
        return Response(TenantSerializer(tenant, context={'request': request}).data)

    @action(detail=True, methods=['post'])
    def cancel(self, request, pk=None):
        tenant = self.get_object()
        tenant = tenant_service.cancel_tenant(tenant=tenant, actor=request.user)
        return Response(TenantSerializer(tenant, context={'request': request}).data)

    # ─────────────────── Entitlements ───────────────────
    @action(detail=True, methods=['get'])
    def features(self, request, pk=None):
        tenant = self.get_object()
        return Response(get_entitlements(tenant))

    # ─────────────────── Package assignment ───────────────────
    @action(detail=True, methods=['post'], url_path='assign-package')
    def assign_package(self, request, pk=None):
        tenant = self.get_object()
        serializer = AssignPackageSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        sub = assign_package(
            tenant=tenant,
            actor=request.user,
            **serializer.validated_data,
        )
        from control.serializers import SubscriptionSerializer
        return Response(
            SubscriptionSerializer(sub, context={'request': request}).data,
            status=status.HTTP_201_CREATED,
        )

    # ─────────────────── Overrides ───────────────────
    @action(detail=True, methods=['get', 'post'])
    def overrides(self, request, pk=None):
        tenant = self.get_object()
        if request.method == 'GET':
            qs = TenantFeatureOverride.objects.filter(tenant=tenant)
            return Response(TenantOverrideSerializer(qs, many=True).data)

        serializer = TenantOverrideUpsertSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        override = upsert_override(
            tenant=tenant, actor=request.user, **serializer.validated_data,
        )
        return Response(
            TenantOverrideSerializer(override).data,
            status=status.HTTP_200_OK,
        )

    @action(
        detail=True, methods=['patch', 'delete'],
        url_path=r'overrides/(?P<feature_code>[\w\-]+)',
    )
    def mutate_override(self, request, pk=None, feature_code=None):
        tenant = self.get_object()
        if request.method.lower() == 'delete':
            remove_override(
                tenant=tenant, feature_code=feature_code, actor=request.user,
            )
            return Response(status=status.HTTP_204_NO_CONTENT)

        payload = {'feature_code': feature_code, **request.data}
        serializer = TenantOverrideUpsertSerializer(data=payload, partial=True)
        serializer.is_valid(raise_exception=True)
        override = upsert_override(
            tenant=tenant, actor=request.user, **serializer.validated_data,
        )
        return Response(TenantOverrideSerializer(override).data)
