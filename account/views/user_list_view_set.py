from rest_framework import viewsets, mixins
from rest_framework.permissions import IsAuthenticated
from control.context import get_current_tenant
from account.permissions import IsTenantStaff
from account.models import User
from account.serializers import UserMinSerializer


class UserListViewSet(mixins.ListModelMixin, viewsets.GenericViewSet):
    """Lightweight read-only viewset for user dropdowns/selectors."""
    queryset = User.objects.order_by('username')
    serializer_class = UserMinSerializer
    permission_classes = (IsAuthenticated, IsTenantStaff)
    pagination_class = None

    def get_queryset(self):
        tenant = get_current_tenant()
        if tenant is None:
            return User.objects.none()
        return self.queryset.filter(
            tenant_memberships__tenant=tenant,
            tenant_memberships__is_active=True,
        ).distinct()
