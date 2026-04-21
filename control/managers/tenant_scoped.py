from django.db import models

from control.context import get_current_tenant


class TenantScopedManager(models.Manager):
    """
    Manager that transparently scopes queries to the tenant set on
    ``control.context.current_tenant``.

    The tenant plane is not implemented yet. Until it is, any code that
    calls ``.objects`` on a tenant-scoped model without a current tenant
    set will raise ``RuntimeError`` - this is intentional and fails loud
    so we never silently leak data across tenants.

    Platform code must use the ``all_objects`` escape-hatch manager.
    """

    def get_queryset(self):
        tenant = get_current_tenant()
        if tenant is None:
            raise RuntimeError(
                'TenantScopedManager accessed without a current tenant. '
                'Use Model.all_objects for platform-plane queries.'
            )
        return super().get_queryset().filter(tenant=tenant)
