from rest_framework import serializers

from control.models import Feature, Package, PackageFeature
from util.mixin.audit_mixin import AuditMixin


class PackageFeatureSerializer(serializers.ModelSerializer):
    feature = serializers.PrimaryKeyRelatedField(queryset=Feature.objects.all())
    feature_code = serializers.CharField(source='feature.code', read_only=True)
    feature_name = serializers.CharField(source='feature.name', read_only=True)

    class Meta:
        model = PackageFeature
        fields = ('id', 'feature', 'feature_code', 'feature_name', 'limit_value')


class PackageSerializer(AuditMixin, serializers.ModelSerializer):
    features = PackageFeatureSerializer(
        source='package_features', many=True, read_only=True,
    )

    class Meta:
        model = Package
        fields = (
            'id', 'code', 'name', 'description', 'currency',
            'price_monthly', 'price_yearly',
            'is_public', 'is_active', 'sort_order',
            'features',
        )
