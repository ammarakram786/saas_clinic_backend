from django.contrib.auth.password_validation import validate_password
from rest_framework import serializers

from platform_ctrl.models import PlatformPermission, PlatformRole, PlatformUser


class PlatformPermissionSerializer(serializers.ModelSerializer):
    class Meta:
        model = PlatformPermission
        fields = ('id', 'code_name', 'name', 'module', 'description')


class PlatformRoleSerializer(serializers.ModelSerializer):
    permissions = PlatformPermissionSerializer(many=True, read_only=True)
    permission_ids = serializers.PrimaryKeyRelatedField(
        queryset=PlatformPermission.objects.all(),
        many=True, write_only=True, source='permissions', required=False,
    )

    class Meta:
        model = PlatformRole
        fields = (
            'id', 'name', 'code_name', 'description',
            'permissions', 'permission_ids',
        )


class PlatformUserSerializer(serializers.ModelSerializer):
    role = serializers.PrimaryKeyRelatedField(
        queryset=PlatformRole.objects.all(), allow_null=True, required=False,
    )
    role_detail = PlatformRoleSerializer(source='role', read_only=True)
    permissions = serializers.SerializerMethodField()

    class Meta:
        model = PlatformUser
        fields = (
            'id', 'email', 'full_name', 'is_active', 'mfa_enabled',
            'role', 'role_detail', 'permissions',
            'last_login_ip', 'last_login_at',
            'created_at', 'updated_at',
        )
        read_only_fields = (
            'id', 'last_login_ip', 'last_login_at', 'created_at', 'updated_at',
        )

    def get_permissions(self, instance):
        if not instance.role_id:
            return []
        return list(instance.role.permissions.values_list('code_name', flat=True))


class PlatformUserCreateSerializer(serializers.ModelSerializer):
    password = serializers.CharField(
        write_only=True, required=True, validators=[validate_password],
    )
    role = serializers.PrimaryKeyRelatedField(
        queryset=PlatformRole.objects.all(), allow_null=True, required=False,
    )

    class Meta:
        model = PlatformUser
        fields = (
            'id', 'email', 'full_name', 'password',
            'is_active', 'mfa_enabled', 'role',
        )
        read_only_fields = ('id',)

    def create(self, validated_data):
        password = validated_data.pop('password')
        user = PlatformUser(**validated_data)
        user.set_password(password)
        user.save()
        return user
