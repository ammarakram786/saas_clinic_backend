import uuid

from django.core.validators import RegexValidator
from django.db import models

from util.mixin.base_mixin import BaseMixin


slug_validator = RegexValidator(
    regex=r'^[a-z0-9][a-z0-9\-]{1,62}[a-z0-9]$',
    message='Slug must be lowercase, 3-64 chars, alphanumeric or hyphen.',
)


class TenantStatus(models.TextChoices):
    TRIAL = 'TRIAL', 'Trial'
    ACTIVE = 'ACTIVE', 'Active'
    SUSPENDED = 'SUSPENDED', 'Suspended'
    CANCELLED = 'CANCELLED', 'Cancelled'


class Tenant(BaseMixin):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=255)
    slug = models.SlugField(
        max_length=64, unique=True, validators=[slug_validator], db_index=True,
    )
    status = models.CharField(
        max_length=20, choices=TenantStatus.choices, default=TenantStatus.TRIAL,
    )
    timezone = models.CharField(max_length=64, default='UTC')
    country = models.CharField(max_length=2, null=True, blank=True)

    contact_email = models.EmailField(null=True, blank=True)
    contact_phone = models.CharField(max_length=32, null=True, blank=True)

    branding = models.JSONField(default=dict, blank=True)
    settings = models.JSONField(default=dict, blank=True)
    limits_snapshot = models.JSONField(default=dict, blank=True)

    onboarded_at = models.DateTimeField(null=True, blank=True)
    trial_ends_at = models.DateTimeField(null=True, blank=True)
    suspended_at = models.DateTimeField(null=True, blank=True)
    cancelled_at = models.DateTimeField(null=True, blank=True)
    suspended_reason = models.TextField(null=True, blank=True)

    internal_notes = models.TextField(null=True, blank=True)

    class Meta:
        db_table = 'platform_tenant'
        verbose_name = 'Tenant'
        verbose_name_plural = 'Tenants'
        indexes = [
            models.Index(fields=['status']),
            models.Index(fields=['slug']),
        ]

    def __str__(self):
        return self.name
