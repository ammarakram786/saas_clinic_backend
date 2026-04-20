from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from account.util import unset_cookies
from account.serializers import LogoutSerializer


class LogoutView(APIView):

    permission_classes = (IsAuthenticated, )

    def post(self, request):
        serializer = LogoutSerializer(data=request.COOKIES, context={'request': request})
        serializer.is_valid(raise_exception=True)

        response = Response()
        unset_cookies(response)
        response.data = {"msg": "Logout successfully"}
        response.status_code = status.HTTP_204_NO_CONTENT

        return response
