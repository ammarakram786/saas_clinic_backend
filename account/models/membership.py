from django.db import models

from util.mixin.base_mixin import BaseMixin


class TenantMembership(BaseMixin):
    user = models.ForeignKey(
        'account.User',
        on_delete=models.CASCADE,
        related_name='tenant_memberships',
    )
    tenant = models.ForeignKey(
        'control.Tenant',
        on_delete=models.CASCADE,
        related_name='staff_memberships',
    )
    role = models.ForeignKey(
        'account.Role',
        on_delete=models.SET_NULL,
        related_name='tenant_memberships',
        null=True,
        blank=True,
    )
    is_active = models.BooleanField(default=True, db_index=True)
    joined_at = models.DateTimeField(auto_now_add=True)
    invited_by = models.ForeignKey(
        'account.User',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='invited_tenant_memberships',
    )
    meta = models.JSONField(default=dict, blank=True)

    class Meta:
        db_table = 'tenant_memberships'
        verbose_name = 'Tenant Membership'
        verbose_name_plural = 'Tenant Memberships'
        constraints = [
            models.UniqueConstraint(
                fields=['user', 'tenant'],
                name='uniq_tenant_membership_user_tenant',
            )
        ]
        indexes = [
            models.Index(fields=['tenant', 'is_active']),
            models.Index(fields=['user', 'is_active']),
        ]

    def __str__(self):
        return f'{self.user_id}:{self.tenant_id}'
