from django.conf import settings
from rest_framework_simplejwt.tokens import RefreshToken


def get_tokens_for_user(user, tenant_id=None, membership_id=None):
    """Generate JWT access and refresh tokens for a user."""
    refresh = RefreshToken.for_user(user)
    if tenant_id is not None:
        refresh['tenant_id'] = str(tenant_id)
    if membership_id is not None:
        refresh['membership_id'] = str(membership_id)
    return {
        'access': str(refresh.access_token),
        'refresh': str(refresh),
    }


def _max_age(lifetime):
    return int(lifetime.total_seconds())


def set_access_cookies(response, access_token):
    response.set_cookie(
        key=settings.SIMPLE_JWT['AUTH_COOKIE'],
        value=access_token,
        max_age=_max_age(settings.SIMPLE_JWT['ACCESS_TOKEN_LIFETIME']),
        secure=settings.SIMPLE_JWT['AUTH_COOKIE_SECURE'],
        httponly=settings.SIMPLE_JWT['AUTH_COOKIE_HTTP_ONLY'],
        samesite=settings.SIMPLE_JWT['AUTH_COOKIE_SAMESITE'],
        path=settings.SIMPLE_JWT['AUTH_COOKIE_PATH'],
    )


def set_refresh_cookies(response, refresh_token):
    response.set_cookie(
        key=settings.SIMPLE_JWT['AUTH_COOKIE_REFRESH'],
        value=refresh_token,
        max_age=_max_age(settings.SIMPLE_JWT['REFRESH_TOKEN_LIFETIME']),
        secure=settings.SIMPLE_JWT['AUTH_COOKIE_SECURE'],
        httponly=settings.SIMPLE_JWT['AUTH_COOKIE_HTTP_ONLY'],
        samesite=settings.SIMPLE_JWT['AUTH_COOKIE_SAMESITE'],
        path=settings.SIMPLE_JWT['AUTH_COOKIE_PATH'],
    )


def unset_cookies(response):
    response.delete_cookie(
        key=settings.SIMPLE_JWT['AUTH_COOKIE'],
        path=settings.SIMPLE_JWT['AUTH_COOKIE_PATH'],
        samesite=settings.SIMPLE_JWT['AUTH_COOKIE_SAMESITE'],
    )
    response.delete_cookie(
        key=settings.SIMPLE_JWT['AUTH_COOKIE_REFRESH'],
        path=settings.SIMPLE_JWT['AUTH_COOKIE_PATH'],
        samesite=settings.SIMPLE_JWT['AUTH_COOKIE_SAMESITE'],
    )


def combine_role_permissions(role):
    if not role:
        return []
    return list(role.permissions.values_list('code_name', flat=True))
