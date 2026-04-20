"""
Platform-plane middleware.

``TenantMiddleware`` resolves the current tenant (from JWT claim or subdomain).
For ``/api/platform/*`` routes the tenant is explicitly left unset so the
platform plane can freely query across tenants via ``all_objects`` managers.

``AuditContextMiddleware`` captures request IP, UA and a request-id so
signal-based audit logging can attribute records without passing the
request object around.
"""

import uuid

from .context import (
    set_current_tenant,
    reset_current_tenant,
    set_audit_context,
    reset_audit_context,
)


PLATFORM_URL_PREFIX = '/api/platform/'


def _client_ip(request):
    xff = request.META.get('HTTP_X_FORWARDED_FOR')
    if xff:
        return xff.split(',')[0].strip()
    return request.META.get('REMOTE_ADDR')


class TenantMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        token = set_current_tenant(None)
        try:
            if not request.path.startswith(PLATFORM_URL_PREFIX):
                tenant = self._resolve_tenant(request)
                if tenant is not None:
                    set_current_tenant(tenant)
            return self.get_response(request)
        finally:
            reset_current_tenant(token)

    def _resolve_tenant(self, request):
        """
        Tenant plane is not implemented yet. When it is, resolve a tenant
        from a JWT claim on ``request.auth`` or a subdomain on ``Host``
        and return the ``Tenant`` instance, or ``None`` if unresolvable.
        """
        return None


class AuditContextMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        request_id = request.META.get('HTTP_X_REQUEST_ID') or uuid.uuid4().hex
        ctx = {
            'ip': _client_ip(request),
            'user_agent': (request.META.get('HTTP_USER_AGENT') or '')[:500],
            'request_id': request_id,
        }
        request.request_id = request_id
        token = set_audit_context(ctx)
        try:
            response = self.get_response(request)
            response['X-Request-ID'] = request_id
            return response
        finally:
            reset_audit_context(token)
