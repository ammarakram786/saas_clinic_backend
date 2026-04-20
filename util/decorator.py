from functools import wraps
from rest_framework.exceptions import PermissionDenied


def route_permissions(permissions):
    def decorator(view_func):
        @wraps(view_func)
        def _wrapper(self, request, *args, **kwargs):
            user = request.user
            if not user or not user.is_authenticated or not hasattr(user, 'role') or not user.role:
                raise PermissionDenied("You do not have an assigned role.")
            has_permission = user.role.permissions.filter(
                code_name__in=permissions
            ).exists()
            if has_permission:
                return view_func(self, request, *args, **kwargs)
            raise PermissionDenied("You do not have permission to perform this action.")

        return _wrapper
    return decorator