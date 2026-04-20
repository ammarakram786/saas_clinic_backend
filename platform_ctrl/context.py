"""
Request-scoped context vars.

`current_tenant` is resolved by ``TenantMiddleware`` for tenant-plane requests
and left unset for platform-plane requests. Models that inherit
``TenantScopedModel`` read this when saving.

`audit_context` carries IP, user-agent, and request id for audit logging.
"""

from contextvars import ContextVar


_current_tenant: ContextVar = ContextVar('current_tenant', default=None)
_audit_context: ContextVar = ContextVar('audit_context', default=None)


def get_current_tenant():
    return _current_tenant.get()


def set_current_tenant(tenant):
    return _current_tenant.set(tenant)


def reset_current_tenant(token):
    _current_tenant.reset(token)


def get_audit_context():
    return _audit_context.get() or {}


def set_audit_context(ctx: dict):
    return _audit_context.set(ctx or {})


def reset_audit_context(token):
    _audit_context.reset(token)
