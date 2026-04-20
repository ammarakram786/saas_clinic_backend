from django.contrib.auth.hashers import check_password
from rest_framework import serializers
from rest_framework_simplejwt.exceptions import TokenError

from platform_ctrl.authentication import PlatformRefreshToken
from platform_ctrl.models import PlatformUser


class PlatformLoginSerializer(serializers.Serializer):
    email = serializers.EmailField(required=True)
    password = serializers.CharField(required=True, max_length=255, write_only=True)

    def validate(self, attrs):
        email = attrs['email'].lower().strip()
        password = attrs['password']

        try:
            user = PlatformUser.objects.get(email__iexact=email)
        except PlatformUser.DoesNotExist:
            raise serializers.ValidationError({'msg': 'Invalid credentials.'})

        if not user.is_active:
            raise serializers.ValidationError({'msg': 'Account is inactive.'})

        if not check_password(password, user.password):
            raise serializers.ValidationError({'msg': 'Invalid credentials.'})

        attrs['user'] = user
        return attrs


class PlatformRefreshSerializer(serializers.Serializer):
    """
    Validates the refresh token from the ``platform_refresh`` cookie and
    exposes it as ``refresh`` on validated_data.
    """

    platform_refresh = serializers.CharField(required=True, write_only=True)

    def validate(self, attrs):
        raw = attrs.get('platform_refresh')
        try:
            refresh = PlatformRefreshToken(raw)
        except TokenError:
            raise serializers.ValidationError({'msg': 'Bad token.'})
        attrs['refresh'] = refresh
        return attrs


class PlatformLogoutSerializer(serializers.Serializer):
    """
    Accepts the refresh token. Blacklisting is performed in the view,
    keeping the serializer side-effect free.
    """

    platform_refresh = serializers.CharField(required=False, allow_blank=True)
