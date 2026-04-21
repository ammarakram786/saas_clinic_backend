from django.conf import settings


def _max_age(lifetime):
    return int(lifetime.total_seconds())


def set_platform_access_cookie(response, access_token):
    cfg = settings.PLATFORM_JWT
    response.set_cookie(
        key=cfg['AUTH_COOKIE'],
        value=access_token,
        max_age=_max_age(cfg['ACCESS_TOKEN_LIFETIME']),
        secure=cfg['AUTH_COOKIE_SECURE'],
        httponly=cfg['AUTH_COOKIE_HTTP_ONLY'],
        samesite=cfg['AUTH_COOKIE_SAMESITE'],
        path=cfg['AUTH_COOKIE_PATH'],
    )


def set_platform_refresh_cookie(response, refresh_token):
    cfg = settings.PLATFORM_JWT
    response.set_cookie(
        key=cfg['AUTH_COOKIE_REFRESH'],
        value=refresh_token,
        max_age=_max_age(cfg['REFRESH_TOKEN_LIFETIME']),
        secure=cfg['AUTH_COOKIE_SECURE'],
        httponly=cfg['AUTH_COOKIE_HTTP_ONLY'],
        samesite=cfg['AUTH_COOKIE_SAMESITE'],
        path=cfg['AUTH_COOKIE_PATH'],
    )


def unset_platform_cookies(response):
    cfg = settings.PLATFORM_JWT
    response.delete_cookie(
        key=cfg['AUTH_COOKIE'],
        path=cfg['AUTH_COOKIE_PATH'],
        samesite=cfg['AUTH_COOKIE_SAMESITE'],
    )
    response.delete_cookie(
        key=cfg['AUTH_COOKIE_REFRESH'],
        path=cfg['AUTH_COOKIE_PATH'],
        samesite=cfg['AUTH_COOKIE_SAMESITE'],
    )
