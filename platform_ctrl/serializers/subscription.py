from rest_framework import serializers

from platform_ctrl.models import Package, TenantSubscription
from platform_ctrl.models.subscription import BillingCycle
from platform_ctrl.serializers.tenant import TenantMinSerializer
from util.mixin.audit_mixin import AuditMixin


class SubscriptionSerializer(AuditMixin, serializers.ModelSerializer):
    tenant = TenantMinSerializer(read_only=True)
    package_code = serializers.CharField(source='package.code', read_only=True)
    package_name = serializers.CharField(source='package.name', read_only=True)

    class Meta:
        model = TenantSubscription
        fields = (
            'id', 'tenant', 'package', 'package_code', 'package_name',
            'billing_cycle', 'status',
            'starts_at', 'ends_at', 'auto_renew',
            'feature_snapshot',
        )
        read_only_fields = ('feature_snapshot', 'status')


class AssignPackageSerializer(serializers.Serializer):
    package_id = serializers.PrimaryKeyRelatedField(
        queryset=Package.objects.all(), source='package',
    )
    billing_cycle = serializers.ChoiceField(
        choices=BillingCycle.choices, default=BillingCycle.MONTHLY,
    )
    starts_at = serializers.DateTimeField(required=False, allow_null=True)
    ends_at = serializers.DateTimeField(required=False, allow_null=True)
    auto_renew = serializers.BooleanField(required=False, default=True)
