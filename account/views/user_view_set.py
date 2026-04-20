from rest_framework import status
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from account.models import User
from account.serializers import UserSerializer, ChangePasswordSerializer
from account.filters import UserFilter
from .base_view import BaseAuditViewSet


class UserViewSet(BaseAuditViewSet):
    queryset = User.objects.filter(role__code_name='su').order_by('-id')
    serializer_class = UserSerializer
    filterset_class = UserFilter

    permissions_map = {
        'list': ['read_user'],
        'retrieve': ['read_user'],
        'create': ['create_user'],
        'update': ['update_user'],
        'partial_update': ['update_user'],
        'destroy': ['delete_user'],
    }

    def get_queryset(self):
        return super().get_queryset()

    def get_serializer_class(self):
        return UserSerializer


    @action(detail=False, methods=['post'], url_path='change-password', url_name='change_password', permission_classes=[IsAuthenticated])
    def change_password(self, request):
        serializer = ChangePasswordSerializer(data=request.data, context={'request': request})
        if serializer.is_valid():
            user = request.user
            user.set_password(serializer.validated_data['new_password'])
            user.initial_reset = True
            user.save()
            return Response({"detail": "Password has been changed successfully."}, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


    
