from rest_framework import permissions


class DynamicRolePermission(permissions.BasePermission):
    """
    Action-based RBAC backed by a `role.permissions` M2M whose rows have a
    `code_name` column. Fails closed: if an action has no mapping we deny.
    """

    def has_permission(self, request, view):
        perm_map = getattr(view, 'permissions_map', {})
        action = getattr(view, 'action', None)

        if action is None:
            return False

        action_perms = perm_map.get(action)
        if not action_perms:
            return False

        user = request.user
        if not user or not user.is_authenticated:
            return False

        role = getattr(user, 'role', None)
        if role is None:
            return False

        return role.permissions.filter(code_name__in=action_perms).exists()
