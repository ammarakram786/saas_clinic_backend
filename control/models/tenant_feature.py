from django.db import models

from util.mixin.base_mixin import BaseMixin


class TenantFeatureOverride(BaseMixin):
    """
    Per-tenant grant or denial that shadows the active subscription's
    ``feature_snapshot``. Used for manual adjustments by platform staff.
    """

    tenant = models.ForeignKey(
        'control.Tenant', on_delete=models.PROTECT, related_name='feature_overrides',
    )
    feature = models.ForeignKey(
        'control.Feature', on_delete=models.PROTECT, related_name='overrides',
    )
    is_enabled = models.BooleanField(default=True)
    limit_value = models.IntegerField(null=True, blank=True)
    expires_at = models.DateTimeField(null=True, blank=True)
    reason = models.TextField(blank=True, default='')

    class Meta:
        db_table = 'platform_tenant_feature_override'
        verbose_name = 'Tenant Feature Override'
        verbose_name_plural = 'Tenant Feature Overrides'
        constraints = [
            models.UniqueConstraint(
                fields=['tenant', 'feature'], name='uniq_tenant_feature_override',
            ),
        ]

    def __str__(self):
        return f'{self.tenant.slug}:{self.feature.code}'
