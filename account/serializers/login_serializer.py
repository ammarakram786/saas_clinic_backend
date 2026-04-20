from django.contrib.auth import authenticate
from rest_framework import serializers


class LoginSerializer(serializers.Serializer):
    username = serializers.CharField(max_length=255, required=True)
    password = serializers.CharField(max_length=255, required=True)

    def validate(self, attrs):
        username = attrs.get('username', None)
        password = attrs.get("password", None)

        if username and password:
            user = authenticate(username=username, password=password)
            if not user:
                raise serializers.ValidationError({'msg': 'Invalid credentials.'})
        else:
            raise serializers.ValidationError({'msg': 'Invalid data.'})

        attrs['user'] = user
        return attrs
