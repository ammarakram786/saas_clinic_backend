from rest_framework import serializers

from platform_ctrl.models import Feature
from util.mixin.audit_mixin import AuditMixin


class FeatureSerializer(AuditMixin, serializers.ModelSerializer):
    class Meta:
        model = Feature
        fields = (
            'id', 'code', 'name', 'description', 'category', 'is_active',
        )
