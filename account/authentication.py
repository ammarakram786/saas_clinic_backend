from django.conf import settings
from rest_framework_simplejwt.authentication import JWTAuthentication


class JWTCookieAuthentication(JWTAuthentication):
    """
    Custom JWT authentication that reads the access token from an HttpOnly cookie
    instead of the Authorization header.
    """

    def authenticate(self, request):
        cookie_name = settings.SIMPLE_JWT.get('AUTH_COOKIE')
        raw_token = request.COOKIES.get(cookie_name)

        if raw_token is None:
            return None

        validated_token = self.get_validated_token(raw_token)
        return self.get_user(validated_token), validated_token
