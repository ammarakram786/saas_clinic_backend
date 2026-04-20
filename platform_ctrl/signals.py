"""
Signal-based audit logging.

``pre_save`` captures the prior state so ``post_save`` can diff
before/after and emit a single ``PlatformAuditLog`` row per mutation.

The audit actor and request metadata are read from ``context.py``
ContextVars (populated by ``AuditContextMiddleware`` and, for actors,
by the DRF auth flow through ``request.user``). We accept ``actor=None``
rather than losing the audit row.
"""

from __future__ import annotations

from django.db.models.signals import post_delete, post_save, pre_save
from django.dispatch import receiver

from platform_ctrl.context import get_audit_context


_PRE_SAVE_SNAPSHOTS: dict = {}

AUDITED_MODEL_LABELS = {
    'platform_ctrl.Tenant',
    'platform_ctrl.Package',
    'platform_ctrl.PackageFeature',
    'platform_ctrl.Feature',
    'platform_ctrl.TenantSubscription',
    'platform_ctrl.TenantFeatureOverride',
    'platform_ctrl.PlatformUser',
    'platform_ctrl.PlatformRole',
}


def _label(model_cls):
    return f'{model_cls._meta.app_label}.{model_cls.__name__}'


def _field_names(instance):
    return [
        f.name for f in instance._meta.get_fields()
        if getattr(f, 'concrete', False) and not f.many_to_many and not f.one_to_many
    ]


def _snapshot(instance):
    try:
        return {name: _serialize_value(getattr(instance, name, None)) for name in _field_names(instance)}
    except Exception:
        return {}


def _serialize_value(value):
    if value is None:
        return None
    if isinstance(value, (str, int, float, bool)):
        return value
    return str(value)


def _diff(before: dict, after: dict) -> dict:
    changes = {}
    keys = set(before.keys()) | set(after.keys())
    for k in keys:
        b = before.get(k)
        a = after.get(k)
        if b != a:
            changes[k] = {'before': b, 'after': a}
    return changes


def _tenant_of(instance, *, action: str):
    """
    Resolve the Tenant this audit row belongs to, if any.

    For a DELETE of the Tenant itself we deliberately return ``None`` - the
    tenant row is already gone, so writing ``PlatformAuditLog.tenant=<that
    pk>`` in the same transaction fails the FK on Postgres. The resource id
    is still captured in ``resource_id`` so the trail isn't lost.
    """
    if instance.__class__.__name__ == 'Tenant':
        if action == 'DELETE':
            return None
        return instance
    direct = getattr(instance, 'tenant', None)
    if direct is not None:
        return direct
    return None


def _write_log(action: str, instance, *, changes: dict | None = None):
    from platform_ctrl.models import PlatformAuditLog

    ctx = get_audit_context()
    PlatformAuditLog.objects.create(
        actor=_current_actor(),
        actor_ip=ctx.get('ip'),
        user_agent=ctx.get('user_agent', '') or '',
        request_id=ctx.get('request_id', '') or '',
        action=action,
        resource_type=instance.__class__.__name__,
        resource_id=str(getattr(instance, 'pk', '') or ''),
        tenant=_tenant_of(instance, action=action),
        changes=changes or {},
    )


def _current_actor():
    """
    Actor resolution is best-effort: we pull the actor from the audit
    context if the request layer stashed it there. Otherwise ``None``.
    """
    ctx = get_audit_context()
    return ctx.get('actor')


@receiver(pre_save)
def _audit_pre_save(sender, instance, **kwargs):
    if _label(sender) not in AUDITED_MODEL_LABELS:
        return
    if instance.pk is None:
        _PRE_SAVE_SNAPSHOTS[id(instance)] = None
        return
    try:
        existing = sender.objects.get(pk=instance.pk)
    except sender.DoesNotExist:
        _PRE_SAVE_SNAPSHOTS[id(instance)] = None
        return
    _PRE_SAVE_SNAPSHOTS[id(instance)] = _snapshot(existing)


@receiver(post_save)
def _audit_post_save(sender, instance, created, **kwargs):
    if _label(sender) not in AUDITED_MODEL_LABELS:
        return
    before = _PRE_SAVE_SNAPSHOTS.pop(id(instance), None)
    after = _snapshot(instance)

    if created:
        _write_log('CREATE', instance, changes={'after': after})
        return

    diff = _diff(before or {}, after)
    if not diff:
        return
    _write_log('UPDATE', instance, changes=diff)


@receiver(post_delete)
def _audit_post_delete(sender, instance, **kwargs):
    if _label(sender) not in AUDITED_MODEL_LABELS:
        return
    _write_log('DELETE', instance, changes={'before': _snapshot(instance)})
