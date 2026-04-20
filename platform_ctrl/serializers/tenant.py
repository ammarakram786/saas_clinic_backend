from rest_framework import serializers

from platform_ctrl.models import Tenant
from util.mixin.audit_mixin import AuditMixin


TENANT_READ_FIELDS = (
    'id', 'name', 'slug', 'status',
    'timezone', 'country',
    'contact_email', 'contact_phone',
    'branding', 'settings', 'limits_snapshot',
    'onboarded_at', 'trial_ends_at',
    'suspended_at', 'suspended_reason', 'cancelled_at',
    'internal_notes', 'is_active',
)

TENANT_WRITE_FIELDS = (
    'name', 'slug', 'timezone', 'country',
    'contact_email', 'contact_phone',
    'branding', 'settings',
    'trial_ends_at', 'internal_notes',
)


class TenantSerializer(AuditMixin, serializers.ModelSerializer):
    class Meta:
        model = Tenant
        fields = TENANT_READ_FIELDS
        read_only_fields = (
            'id', 'status', 'limits_snapshot',
            'onboarded_at', 'suspended_at', 'suspended_reason', 'cancelled_at',
        )


class TenantCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tenant
        fields = TENANT_WRITE_FIELDS


class TenantMinSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tenant
        fields = ('id', 'name', 'slug', 'status')
