from rest_framework import status
from rest_framework.decorators import action
from rest_framework.response import Response

from control.models import Package
from control.serializers import PackageSerializer, PackageFeatureSerializer
from control.services import package_service
from control.views.platform_base import PlatformViewSet


class PackageViewSet(PlatformViewSet):
    queryset = Package.objects.all().prefetch_related('package_features__feature')
    serializer_class = PackageSerializer
    search_fields = ('code', 'name')
    ordering_fields = ('code', 'name', 'sort_order', 'is_active')
    filterset_fields = ('is_active', 'is_public', 'currency')

    permissions_map = {
        'list':           ['platform.package.read'],
        'retrieve':       ['platform.package.read'],
        'create':         ['platform.package.manage'],
        'update':         ['platform.package.manage'],
        'partial_update': ['platform.package.manage'],
        'destroy':        ['platform.package.manage'],
        'set_features':   ['platform.package.manage'],
    }

    def create(self, request, *args, **kwargs):
        features = request.data.get('features') or []
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = {k: v for k, v in serializer.validated_data.items() if k != 'package_features'}
        package = package_service.create_package(
            data=data, features=features, actor=request.user,
        )
        return Response(
            PackageSerializer(package).data, status=status.HTTP_201_CREATED,
        )

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        package = self.get_object()
        serializer = self.get_serializer(package, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        data = {k: v for k, v in serializer.validated_data.items() if k != 'package_features'}
        package = package_service.update_package(
            package=package, data=data, actor=request.user,
        )

        if 'features' in request.data:
            package = package_service.set_package_features(
                package=package, features=request.data['features'], actor=request.user,
            )

        return Response(PackageSerializer(package).data)

    @action(detail=True, methods=['post'], url_path='features')
    def set_features(self, request, pk=None):
        package = self.get_object()
        features = request.data.get('features', request.data)
        if not isinstance(features, list):
            return Response(
                {'msg': 'Expected a list of {feature, limit_value} entries.'},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # Validate via serializer row-by-row for nicer error messages.
        for row in features:
            PackageFeatureSerializer(data=row).is_valid(raise_exception=True)

        package = package_service.set_package_features(
            package=package, features=features, actor=request.user,
        )
        return Response(PackageSerializer(package).data)
