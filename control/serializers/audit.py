from rest_framework import serializers

from control.models import PlatformAuditLog


class PlatformAuditLogSerializer(serializers.ModelSerializer):
    actor_email = serializers.CharField(source='actor.email', read_only=True, default=None)
    tenant_slug = serializers.CharField(source='tenant.slug', read_only=True, default=None)

    class Meta:
        model = PlatformAuditLog
        fields = (
            'id', 'action',
            'actor', 'actor_email', 'actor_ip', 'user_agent', 'request_id',
            'resource_type', 'resource_id',
            'tenant', 'tenant_slug',
            'changes', 'created_at',
        )
        read_only_fields = fields
