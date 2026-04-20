"""
Placeholder module so the ``platform_ctrl.views`` package import chain is
stable. Overrides are driven through actions on ``TenantViewSet``, not a
standalone viewset.
"""

from rest_framework import viewsets


class TenantOverrideViewSet(viewsets.ViewSet):
    """Unused. See ``TenantViewSet.overrides`` / ``TenantViewSet.mutate_override``."""
