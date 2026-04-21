from django.conf import settings
from django.middleware import csrf
from django.utils import timezone
from rest_framework import status
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.throttling import ScopedRateThrottle
from rest_framework.views import APIView
from rest_framework_simplejwt.exceptions import TokenError

from control.authentication import (
    PlatformRefreshToken,
    get_platform_tokens_for_user,
)
from control.permissions import IsPlatformStaff
from control.serializers import (
    PlatformLoginSerializer,
    PlatformRefreshSerializer,
    PlatformLogoutSerializer,
    PlatformUserSerializer,
)
from control.util import (
    set_platform_access_cookie,
    set_platform_refresh_cookie,
    unset_platform_cookies,
)


def _client_ip(request):
    xff = request.META.get('HTTP_X_FORWARDED_FOR')
    if xff:
        return xff.split(',')[0].strip()
    return request.META.get('REMOTE_ADDR')


class PlatformLoginView(APIView):
    authentication_classes = ()
    permission_classes = (AllowAny,)
    throttle_classes = (ScopedRateThrottle,)
    throttle_scope = 'platform_login'

    def post(self, request):
        serializer = PlatformLoginSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data['user']

        user.last_login = timezone.now()
        user.last_login_at = timezone.now()
        user.last_login_ip = _client_ip(request)
        user.save(update_fields=['last_login', 'last_login_at', 'last_login_ip'])

        tokens = get_platform_tokens_for_user(user)

        response = Response(status=status.HTTP_200_OK)
        set_platform_access_cookie(response, tokens['access'])
        set_platform_refresh_cookie(response, tokens['refresh'])
        response['X-CSRFToken'] = csrf.get_token(request)

        user_data = PlatformUserSerializer(user).data
        response.data = {'msg': 'Login successfully', 'user': user_data}
        return response


class PlatformRefreshView(APIView):
    authentication_classes = ()
    permission_classes = (AllowAny,)
    throttle_classes = (ScopedRateThrottle,)
    throttle_scope = 'platform_refresh'

    def post(self, request):
        cookie_name = settings.PLATFORM_JWT['AUTH_COOKIE_REFRESH']
        raw = request.COOKIES.get(cookie_name)
        serializer = PlatformRefreshSerializer(data={'platform_refresh': raw})
        serializer.is_valid(raise_exception=True)
        refresh = serializer.validated_data['refresh']

        response = Response(status=status.HTTP_200_OK)
        set_platform_access_cookie(response, str(refresh.access_token))

        cfg = settings.PLATFORM_JWT
        if cfg.get('ROTATE_REFRESH_TOKENS'):
            if cfg.get('BLACKLIST_AFTER_ROTATION'):
                try:
                    refresh.blacklist()
                except AttributeError:
                    pass
            refresh.set_jti()
            refresh.set_exp()
            refresh.set_iat()
            set_platform_refresh_cookie(response, str(refresh))

        return response


class PlatformLogoutView(APIView):
    permission_classes = (IsAuthenticated, IsPlatformStaff)

    def post(self, request):
        raw = request.COOKIES.get(settings.PLATFORM_JWT['AUTH_COOKIE_REFRESH'])
        serializer = PlatformLogoutSerializer(data={'platform_refresh': raw or ''})
        serializer.is_valid(raise_exception=True)

        if raw:
            try:
                PlatformRefreshToken(raw).blacklist()
            except (TokenError, AttributeError):
                pass

        response = Response(
            {'msg': 'Logout successfully'}, status=status.HTTP_204_NO_CONTENT,
        )
        unset_platform_cookies(response)
        return response


class CurrentPlatformUserView(APIView):
    permission_classes = (IsAuthenticated, IsPlatformStaff)

    def get(self, request):
        data = PlatformUserSerializer(request.user).data
        return Response(data)
