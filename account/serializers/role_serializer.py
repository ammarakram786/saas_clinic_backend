from rest_framework import serializers
from account.models import Role, Permission
from .permission_serializer import PermissionSerializer
from util.mixin.audit_mixin import AuditMixin


class RoleSerializer(AuditMixin, serializers.ModelSerializer):
    permissions = PermissionSerializer(read_only=True, many=True)
    permissions_id = serializers.PrimaryKeyRelatedField(
        queryset=Permission.objects.all(),
        write_only=True,
        many=True,
        source='permissions',
    )

    class Meta:
        model = Role
        fields = (
            'id', 'name', 'code_name', 'permissions', 'permissions_id'
        )

    def to_representation(self, instance):
        rep = super().to_representation(instance)
        return rep


class RoleMinSerializer(serializers.ModelSerializer):

    class Meta:
        model = Role
        fields = ('id','name')



