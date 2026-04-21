from rest_framework import serializers

from control.models import TenantFeatureOverride


class TenantOverrideSerializer(serializers.ModelSerializer):
    feature_code = serializers.CharField(source='feature.code', read_only=True)
    feature_name = serializers.CharField(source='feature.name', read_only=True)

    class Meta:
        model = TenantFeatureOverride
        fields = (
            'id', 'feature', 'feature_code', 'feature_name',
            'is_enabled', 'limit_value', 'expires_at', 'reason',
            'created_at', 'updated_at',
        )
        read_only_fields = ('id', 'feature', 'created_at', 'updated_at')


class TenantOverrideUpsertSerializer(serializers.Serializer):
    feature_code = serializers.CharField(max_length=64)
    is_enabled = serializers.BooleanField(default=True)
    limit_value = serializers.IntegerField(required=False, allow_null=True)
    expires_at = serializers.DateTimeField(required=False, allow_null=True)
    reason = serializers.CharField(required=False, allow_blank=True, default='')
