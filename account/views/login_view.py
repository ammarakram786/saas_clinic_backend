from django.middleware import csrf
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import AllowAny
from rest_framework.throttling import ScopedRateThrottle

from account.util import set_access_cookies, set_refresh_cookies, get_tokens_for_user, combine_role_permissions
from account.serializers import UserSerializer, LoginSerializer


class LoginView(APIView):
    authentication_classes = ()
    permission_classes = (AllowAny,)
    throttle_classes = (ScopedRateThrottle,)
    throttle_scope = 'login'

    def post(self, request):
        serializer = LoginSerializer(data=request.data, context={'request': request})
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data['user']
        membership = serializer.validated_data['membership']

        response = Response()

        token = get_tokens_for_user(
            user,
            tenant_id=membership.tenant_id,
            membership_id=membership.pk,
        )
        set_access_cookies(response, token['access'])
        set_refresh_cookies(response, token['refresh'])

        response['X-CSRFToken'] = csrf.get_token(request)

        data = UserSerializer(user, context={'request': request}).data
        data['tenant'] = {
            'id': membership.tenant_id,
            'name': membership.tenant.name,
            'slug': membership.tenant.slug,
        }
        data['membership_id'] = membership.pk
        data['permissions'] = combine_role_permissions(membership.role)

        response.status_code = status.HTTP_200_OK
        response.data = {'msg': 'Login successfully', 'user': data}
        return response
