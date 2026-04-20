from rest_framework.generics import ListAPIView
from rest_framework.permissions import IsAuthenticated
from account.models import Permission
from account.serializers import PermissionSerializer

class PermissionListView(ListAPIView):

    def get_queryset(self):
        return Permission.objects.all()

    def get_serializer_class(self):
        return PermissionSerializer

    def get_permissions(self):
        return (IsAuthenticated,)

