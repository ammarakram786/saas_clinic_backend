from django.apps import AppConfig


class PlatformCtrlConfig(AppConfig):
    """
    Django app for the platform control plane.

    Packaged as ``platform_ctrl`` (not ``platform``) to avoid shadowing the
    Python standard library's ``platform`` module. The public URL prefix
    remains ``/api/platform/``.
    """

    default_auto_field = 'django.db.models.BigAutoField'
    name = 'platform_ctrl'
    label = 'platform_ctrl'
    verbose_name = 'Platform Control Plane'

    def ready(self):
        from . import signals  # noqa: F401
