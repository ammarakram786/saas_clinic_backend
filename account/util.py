from django.conf import settings
from rest_framework_simplejwt.tokens import RefreshToken


def get_tokens_for_user(user):
    """Generate JWT access and refresh tokens for a user."""
    refresh = RefreshToken.for_user(user)
    return {
        'access': str(refresh.access_token),
        'refresh': str(refresh),
    }


def set_access_cookies(response, access_token):
    """Set the access token as an HttpOnly cookie."""
    response.set_cookie(
        key=settings.SIMPLE_JWT['AUTH_COOKIE'],
        value=access_token,
        expires=settings.SIMPLE_JWT['ACCESS_TOKEN_LIFETIME'],
        secure=settings.SIMPLE_JWT['AUTH_COOKIE_SECURE'],
        httponly=settings.SIMPLE_JWT['AUTH_COOKIE_HTTP_ONLY'],
        samesite=settings.SIMPLE_JWT['AUTH_COOKIE_SAMESITE'],
        path=settings.SIMPLE_JWT['AUTH_COOKIE_PATH'],
    )


def set_refresh_cookies(response, refresh_token):
    """Set the refresh token as an HttpOnly cookie."""
    response.set_cookie(
        key=settings.SIMPLE_JWT['AUTH_COOKIE_REFRESH'],
        value=refresh_token,
        expires=settings.SIMPLE_JWT['REFRESH_TOKEN_LIFETIME'],
        secure=settings.SIMPLE_JWT['AUTH_COOKIE_SECURE'],
        httponly=settings.SIMPLE_JWT['AUTH_COOKIE_HTTP_ONLY'],
        samesite=settings.SIMPLE_JWT['AUTH_COOKIE_SAMESITE'],
        path=settings.SIMPLE_JWT['AUTH_COOKIE_PATH'],
    )


def unset_cookies(response):
    """Delete both access and refresh token cookies."""
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
    """Return a list of permission code_names for a given role."""
    if not role:
        return []
    return list(role.permissions.values_list('code_name', flat=True))
