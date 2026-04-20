from rest_framework.permissions import BasePermission


class IsPlatformStaff(BasePermission):
    """
    Passes only for authenticated ``PlatformUser`` instances.
    Tenant-plane users (``account.User``) never match.
    """

    message = 'Platform staff credentials required.'

    def has_permission(self, request, view):
        user = getattr(request, 'user', None)
        if user is None or not user.is_authenticated:
            return False

        from platform_ctrl.models import PlatformUser
        return isinstance(user, PlatformUser) and getattr(user, 'is_active', False)
