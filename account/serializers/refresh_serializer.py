from rest_framework_simplejwt.tokens import RefreshToken, TokenError
from rest_framework import serializers


class RefreshSerializer(serializers.Serializer):
    refresh_token = serializers.CharField(max_length=255, required=True)

    def validate(self, attrs):
        refresh_token = attrs.get('refresh_token', None)

        try:
            refresh = RefreshToken(refresh_token)
        except TokenError:
            raise serializers.ValidationError({'msg': 'Bad token.'})

        attrs['refresh'] = refresh
        return attrs
