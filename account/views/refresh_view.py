from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from rest_framework.throttling import ScopedRateThrottle
from django.conf import settings
from account.util import set_access_cookies, set_refresh_cookies
from account.serializers import RefreshSerializer


class RefreshView(APIView):

    authentication_classes = ()
    permission_classes = (AllowAny,)
    throttle_classes = (ScopedRateThrottle,)
    throttle_scope = 'refresh'

    def post(self, request):
        serializer = RefreshSerializer(data=request.COOKIES, context={'request': request})
        serializer.is_valid(raise_exception=True)
        refresh = serializer.validated_data['refresh']

        response = Response()
        set_access_cookies(response, str(refresh.access_token))

        if settings.SIMPLE_JWT['ROTATE_REFRESH_TOKENS']:
            if settings.SIMPLE_JWT['BLACKLIST_AFTER_ROTATION']:
                try:
                    refresh.blacklist()
                except AttributeError:
                    pass

            refresh.set_jti()
            refresh.set_exp()
            refresh.set_iat()

            set_refresh_cookies(response, str(refresh))

        return response

