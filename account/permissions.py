from rest_framework.permissions import BasePermission

from control.context import get_current_tenant


class IsTenantStaff(BasePermission):
    message = 'Tenant staff membership required.'

    def has_permission(self, request, view):
        user = getattr(request, 'user', None)
        if user is None or not user.is_authenticated:
            return False

        from account.models import TenantMembership, User

        if not isinstance(user, User):
            return False

        tenant = get_current_tenant()
        if tenant is None:
            return False

        return TenantMembership.objects.filter(
            user=user,
            tenant=tenant,
            is_active=True,
        ).exists()
