from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated

from control.context import get_audit_context, set_audit_context
from control.pagination import PlatformPagination
from control.permissions import IsPlatformStaff
from util.permissions import DynamicRolePermission


class _PlatformViewSetMixin:
    permission_classes = (IsAuthenticated, IsPlatformStaff, DynamicRolePermission)
    pagination_class = PlatformPagination

    def initial(self, request, *args, **kwargs):
        super().initial(request, *args, **kwargs)
        user = getattr(request, 'user', None)
        if user is not None and user.is_authenticated:
            ctx = dict(get_audit_context())
            ctx['actor'] = user
            set_audit_context(ctx)

    def get_queryset(self):
        """
        Default to the ``all_objects`` manager when the model exposes it
        (i.e. tenant-scoped tables), so the platform plane can see data
        across tenants.
        """
        qs = super().get_queryset()
        manager = getattr(qs.model, 'all_objects', None)
        if manager is not None and qs.model._default_manager.__class__.__name__ == 'TenantScopedManager':
            return manager.all()
        return qs

    def perform_create(self, serializer):
        serializer.save()

    def perform_update(self, serializer):
        serializer.save()


class PlatformViewSet(_PlatformViewSetMixin, viewsets.ModelViewSet):
    """
    Base ModelViewSet for every platform-plane write endpoint.

    Subclasses must set ``queryset``, ``serializer_class`` and
    ``permissions_map`` (action -> list[code_name]).
    """


class PlatformReadOnlyViewSet(_PlatformViewSetMixin, viewsets.ReadOnlyModelViewSet):
    """Read-only variant for list/retrieve-only resources."""
