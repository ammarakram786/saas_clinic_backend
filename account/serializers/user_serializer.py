from rest_framework import serializers
from control.context import get_current_tenant
from account.models import User, TenantMembership
from django.contrib.auth.password_validation import validate_password
from .role_serializer import RoleMinSerializer

class UserSerializer(serializers.ModelSerializer):

    class Meta:
        model = User
        fields = '__all__'
        extra_kwargs = {
            'password': {'write_only': True}
        }


    def to_representation(self, instance):
        rep = super().to_representation(instance)
        rep['role'] = RoleMinSerializer(instance.role).data if instance.role else None
        tenant = get_current_tenant()
        if tenant is not None:
            membership = (
                TenantMembership.objects.select_related('role')
                .filter(user=instance, tenant=tenant, is_active=True)
                .first()
            )
            rep['tenant_role'] = (
                RoleMinSerializer(membership.role).data
                if membership and membership.role else None
            )
        else:
            rep['tenant_role'] = None

        return rep

    def create(self, validated_data):
        password = validated_data.pop('password', None)
        user = User(**validated_data)
        if password:
            user.set_password(password)
        else:
            user.set_unusable_password()
        user.save()
        return user

    def update(self, instance, validated_data):
        password = validated_data.pop('password', None)
        for field, value in validated_data.items():
            setattr(instance, field, value)
        if password:
            instance.set_password(password)
        instance.save()
        return instance


class ChangePasswordSerializer(serializers.Serializer):
    old_password = serializers.CharField(required=True)
    new_password = serializers.CharField(required=True, validators=[validate_password])
    confirm_new_password = serializers.CharField(required=True)

    def validate(self, data):
        if data['new_password'] != data['confirm_new_password']:
            raise serializers.ValidationError({
                "confirm_new_password": "New password fields didn't match."
            })

        user = self.context['request'].user
        if not user.check_password(data['old_password']):
            raise serializers.ValidationError("Old password is not correct.")
        return data



class UserMinSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('id', 'username', 'email')
