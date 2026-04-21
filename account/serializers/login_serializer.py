from django.contrib.auth import authenticate
from rest_framework import serializers

from account.models import TenantMembership

class LoginSerializer(serializers.Serializer):
    username = serializers.CharField(max_length=255, required=True)
    password = serializers.CharField(max_length=255, required=True)
    tenant_slug = serializers.CharField(max_length=64, required=False, allow_blank=True)

    def validate(self, attrs):
        username = attrs.get('username')
        password = attrs.get('password')
        request = self.context.get('request')

        if not username or not password:
            raise serializers.ValidationError({'msg': 'Invalid data.'})

        user = authenticate(request=request, username=username, password=password)
        if not user:
            raise serializers.ValidationError({'msg': 'Invalid credentials.'})

        tenant_slug = (attrs.get('tenant_slug') or '').strip().lower()
        memberships = (
            TenantMembership.objects.select_related('tenant', 'role')
            .filter(user=user, is_active=True, tenant__is_active=True)
        )
        if tenant_slug:
            memberships = memberships.filter(tenant__slug=tenant_slug)

        membership = memberships.order_by('tenant__created_at').first()
        if membership is None:
            raise serializers.ValidationError(
                {'msg': 'No active tenant membership found for this user.'}
            )

        attrs['user'] = user
        attrs['membership'] = membership
        return attrs
