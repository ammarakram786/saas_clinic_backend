import uuid

from django.db import models


class AuditAction(models.TextChoices):
    CREATE = 'CREATE', 'Create'
    UPDATE = 'UPDATE', 'Update'
    DELETE = 'DELETE', 'Delete'
    SUSPEND = 'SUSPEND', 'Suspend'
    ACTIVATE = 'ACTIVATE', 'Activate'
    CANCEL = 'CANCEL', 'Cancel'
    ASSIGN_PACKAGE = 'ASSIGN_PACKAGE', 'Assign Package'
    OVERRIDE_SET = 'OVERRIDE_SET', 'Override Set'
    LOGIN = 'LOGIN', 'Login'
    LOGOUT = 'LOGOUT', 'Logout'


class PlatformAuditLog(models.Model):
    """
    Immutable record of a platform-plane action. Written by signals so
    every mutation is captured without per-view boilerplate.
    """

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    actor = models.ForeignKey(
        'platform_ctrl.PlatformUser', null=True, blank=True,
        on_delete=models.SET_NULL, related_name='+',
    )
    actor_ip = models.GenericIPAddressField(null=True, blank=True)
    user_agent = models.CharField(max_length=512, blank=True, default='')
    request_id = models.CharField(max_length=64, blank=True, default='', db_index=True)

    action = models.CharField(
        max_length=32, choices=AuditAction.choices, db_index=True,
    )
    resource_type = models.CharField(max_length=64, db_index=True)
    resource_id = models.CharField(max_length=64, blank=True, default='', db_index=True)

    tenant = models.ForeignKey(
        'platform_ctrl.Tenant', null=True, blank=True,
        on_delete=models.SET_NULL, related_name='+',
    )

    changes = models.JSONField(default=dict, blank=True)

    created_at = models.DateTimeField(auto_now_add=True, db_index=True)

    class Meta:
        db_table = 'platform_audit_log'
        verbose_name = 'Platform Audit Log'
        verbose_name_plural = 'Platform Audit Logs'
        ordering = ('-created_at',)
        indexes = [
            models.Index(fields=['resource_type', 'resource_id']),
            models.Index(fields=['-created_at']),
        ]

    def __str__(self):
        return f'{self.action} {self.resource_type}:{self.resource_id}'
