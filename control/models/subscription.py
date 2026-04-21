from django.db import models

from util.mixin.base_mixin import BaseMixin


class BillingCycle(models.TextChoices):
    MONTHLY = 'MONTHLY', 'Monthly'
    YEARLY = 'YEARLY', 'Yearly'
    CUSTOM = 'CUSTOM', 'Custom'


class SubscriptionStatus(models.TextChoices):
    TRIAL = 'TRIAL', 'Trial'
    ACTIVE = 'ACTIVE', 'Active'
    PAST_DUE = 'PAST_DUE', 'Past Due'
    CANCELLED = 'CANCELLED', 'Cancelled'
    EXPIRED = 'EXPIRED', 'Expired'


ACTIVE_STATUSES = (SubscriptionStatus.TRIAL, SubscriptionStatus.ACTIVE)


class TenantSubscription(BaseMixin):
    tenant = models.ForeignKey(
        'control.Tenant', on_delete=models.PROTECT, related_name='subscriptions',
    )
    package = models.ForeignKey(
        'control.Package', on_delete=models.PROTECT, related_name='subscriptions',
    )
    billing_cycle = models.CharField(
        max_length=16, choices=BillingCycle.choices, default=BillingCycle.MONTHLY,
    )
    status = models.CharField(
        max_length=16, choices=SubscriptionStatus.choices, default=SubscriptionStatus.TRIAL,
    )
    starts_at = models.DateTimeField()
    ends_at = models.DateTimeField(null=True, blank=True)
    auto_renew = models.BooleanField(default=True)

    feature_snapshot = models.JSONField(
        default=dict, blank=True,
        help_text=(
            "Frozen {feature_code: limit_value|null} at subscription creation. "
            "Package edits never retroactively change an existing subscription."
        ),
    )

    class Meta:
        db_table = 'platform_tenant_subscription'
        verbose_name = 'Tenant Subscription'
        verbose_name_plural = 'Tenant Subscriptions'
        constraints = [
            models.UniqueConstraint(
                fields=['tenant'],
                condition=models.Q(status__in=['TRIAL', 'ACTIVE']),
                name='one_active_subscription_per_tenant',
            ),
        ]
        indexes = [
            models.Index(fields=['tenant', 'status']),
            models.Index(fields=['package', 'status']),
        ]

    def __str__(self):
        return f'{self.tenant.slug}:{self.package.code}:{self.status}'
