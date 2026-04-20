"""
Cookie-based JWT authentication for the platform plane.

- Cookie names: ``platform_access`` / ``platform_refresh`` (distinct from
  the tenant-plane ``access_token`` / ``refresh_token`` so one session
  never shadows the other).
- Token lifetimes and SameSite come from ``settings.PLATFORM_JWT``.
- Tokens carry a ``platform_user_id`` claim so tenant-plane auth and
  platform-plane auth use disjoint claim namespaces.
"""

from django.conf import settings
from django.utils.functional import cached_property
from rest_framework.authentication import BaseAuthentication
from rest_framework.exceptions import AuthenticationFailed
from rest_framework_simplejwt.exceptions import TokenError
from rest_framework_simplejwt.tokens import AccessToken, RefreshToken


PLATFORM_ACCESS_TYPE = 'platform_access'
PLATFORM_REFRESH_TYPE = 'platform_refresh'


class PlatformAccessToken(AccessToken):
    token_type = PLATFORM_ACCESS_TYPE

    @property
    def lifetime(self):
        return settings.PLATFORM_JWT['ACCESS_TOKEN_LIFETIME']

    @classmethod
    def for_user(cls, user):
        token = cls()
        token[settings.PLATFORM_JWT['USER_ID_CLAIM']] = str(user.id)
        return token


class PlatformRefreshToken(RefreshToken):
    token_type = PLATFORM_REFRESH_TYPE
    access_token_class = PlatformAccessToken
    no_copy_claims = (
        'token_type', 'exp', 'jti', 'iat',
    )

    @property
    def lifetime(self):
        return settings.PLATFORM_JWT['REFRESH_TOKEN_LIFETIME']

    @classmethod
    def for_user(cls, user):
        token = cls()
        token[settings.PLATFORM_JWT['USER_ID_CLAIM']] = str(user.id)
        return token

    @property
    def access_token(self):
        access = PlatformAccessToken()
        access.set_exp(from_time=self.current_time)
        for claim, value in self.payload.items():
            if claim in PlatformRefreshToken.no_copy_claims:
                continue
            access[claim] = value
        return access


def get_platform_tokens_for_user(user):
    refresh = PlatformRefreshToken.for_user(user)
    return {
        'access': str(refresh.access_token),
        'refresh': str(refresh),
    }


class PlatformJWTCookieAuthentication(BaseAuthentication):
    """
    Reads a platform access token from the ``platform_access`` cookie.

    Returns ``(PlatformUser, validated_token)`` on success, or ``None`` if
    the cookie is absent (so tenant-plane auth can still run for the same
    request chain).
    """

    @cached_property
    def cookie_name(self):
        return settings.PLATFORM_JWT['AUTH_COOKIE']

    @cached_property
    def user_id_claim(self):
        return settings.PLATFORM_JWT['USER_ID_CLAIM']

    def authenticate(self, request):
        raw = request.COOKIES.get(self.cookie_name)
        if not raw:
            return None

        try:
            token = PlatformAccessToken(raw)
        except TokenError as exc:
            raise AuthenticationFailed(str(exc))

        if token.get('token_type') != PLATFORM_ACCESS_TYPE:
            raise AuthenticationFailed('Invalid platform token type.')

        user_id = token.get(self.user_id_claim)
        if not user_id:
            raise AuthenticationFailed('Platform token missing user claim.')

        from platform_ctrl.models import PlatformUser
        try:
            user = PlatformUser.objects.get(pk=user_id)
        except PlatformUser.DoesNotExist:
            raise AuthenticationFailed('Platform user not found.')

        if not user.is_active:
            raise AuthenticationFailed('Platform user is inactive.')

        return user, token
