from rest_framework import serializers
from account.models import User
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

        return rep


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
        fields = ('id', 'username', 'name')
