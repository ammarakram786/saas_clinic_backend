from rest_framework import serializers
from account.models import Permission


class PermissionSerializer(serializers.ModelSerializer):

    class Meta:
        model = Permission
        fields = (
            'id', 'name', 'code_name', 'module_name', 'description'
        )
