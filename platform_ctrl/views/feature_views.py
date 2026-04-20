from platform_ctrl.models import Feature
from platform_ctrl.serializers import FeatureSerializer
from platform_ctrl.services import feature_service
from platform_ctrl.views.platform_base import PlatformViewSet

from rest_framework import status
from rest_framework.response import Response


class FeatureViewSet(PlatformViewSet):
    queryset = Feature.objects.all().order_by('category', 'code')
    serializer_class = FeatureSerializer
    search_fields = ('code', 'name', 'category')
    ordering_fields = ('code', 'name', 'category', 'is_active')
    filterset_fields = ('is_active', 'category')

    permissions_map = {
        'list':           ['platform.feature.read'],
        'retrieve':       ['platform.feature.read'],
        'create':         ['platform.feature.manage'],
        'update':         ['platform.feature.manage'],
        'partial_update': ['platform.feature.manage'],
        'destroy':        ['platform.feature.manage'],
    }

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        feature = feature_service.create_feature(
            data=serializer.validated_data, actor=request.user,
        )
        return Response(
            FeatureSerializer(feature).data, status=status.HTTP_201_CREATED,
        )

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        feature = self.get_object()
        serializer = self.get_serializer(feature, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        feature = feature_service.update_feature(
            feature=feature, data=serializer.validated_data, actor=request.user,
        )
        return Response(FeatureSerializer(feature).data)

    def destroy(self, request, *args, **kwargs):
        feature = self.get_object()
        feature_service.deactivate_feature(feature=feature, actor=request.user)
        return Response(status=status.HTTP_204_NO_CONTENT)
