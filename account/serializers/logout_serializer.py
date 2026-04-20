from rest_framework_simplejwt.tokens import RefreshToken, TokenError
from rest_framework import serializers


class LogoutSerializer(serializers.Serializer):
    refresh_token = serializers.CharField(max_length=255, required=True)

    def validate(self, attrs):
        refresh_token = attrs.get('refresh_token', None)

        try:
            RefreshToken(refresh_token).blacklist()
        except TokenError:
            raise serializers.ValidationError({'msg': 'Bad token.'})

        return attrs
