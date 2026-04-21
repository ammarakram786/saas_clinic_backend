from django.db import models

from util.mixin.base_mixin import BaseMixin
from control.context import get_current_tenant
from control.managers import TenantScopedManager


class TenantScopedModel(BaseMixin):
    tenant = models.ForeignKey(
        'control.Tenant',
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
                    'control.context.set_current_tenant().'
                )
            self.tenant = tenant
        super().save(*args, **kwargs)
