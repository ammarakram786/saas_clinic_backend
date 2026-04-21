from django.apps import AppConfig


class ControlConfig(AppConfig):
    """
    Django app for the platform control plane.

    Packaged as ``control`` (not ``platform``) to avoid shadowing the
    Python standard library's ``platform`` module. The public URL prefix
    remains ``/api/platform/``.
    """

    default_auto_field = 'django.db.models.BigAutoField'
    name = 'control'
    label = 'control'
    verbose_name = 'Platform Control Plane'

    def ready(self):
        from . import signals  # noqa: F401
