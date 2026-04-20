from django.db import models

from util.mixin.base_mixin import BaseMixin
from platform_ctrl.context import get_current_tenant
from platform_ctrl.managers import TenantScopedManager


class TenantScopedModel(BaseMixin):
    """
    Abstract base for tenant-plane tables. Every row is pinned to a tenant.

    - ``tenant`` FK PROTECT: tenants never dangle; deletion is explicitly
      blocked.
    - ``objects`` auto-filters by the current tenant.
    - ``all_objects`` is the escape hatch for platform-plane code.
    """

    tenant = models.ForeignKey(
        'platform_ctrl.Tenant',
        on_delete=models.PROTECT,
        null=False,
        editable=False,
        db_index=True,
        related_name='+',
    )

    objects = TenantScopedManager()
    all_objects = models.Manager()

    class Meta:
        abstract = True

    def save(self, *args, **kwargs):
        if self._state.adding and self.tenant_id is None:
            tenant = get_current_tenant()
            if tenant is None:
                raise RuntimeError(
                    f'{self.__class__.__name__}.save() called without a '
                    'current tenant. Set one via TenantMiddleware or '
                    'platform_ctrl.context.set_current_tenant().'
                )
            self.tenant = tenant
        super().save(*args, **kwargs)
