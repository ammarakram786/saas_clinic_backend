from rest_framework import permissions

class DynamicRolePermission(permissions.BasePermission):
    def has_permission(self, request, view):
        perm_map = getattr(view, 'permissions_map', {})
        action_perms = perm_map.get(view.action)
        if not action_perms:
            return True
        user = request.user
        if not user.is_authenticated or not user.role:
            return False

        return user.role.permissions.filter(code_name__in=action_perms).exists()