from rest_framework import viewsets, mixins
from rest_framework.permissions import IsAuthenticated
from account.models import User
from account.serializers import UserMinSerializer


class UserListViewSet(mixins.ListModelMixin, viewsets.GenericViewSet):
    """Lightweight read-only viewset for user dropdowns/selectors."""
    queryset = User.objects.exclude(role__code_name='su').order_by('username')
    serializer_class = UserMinSerializer
    permission_classes = (IsAuthenticated,)
    pagination_class = None
