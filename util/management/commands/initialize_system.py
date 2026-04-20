from django.core import management
from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = 'Runs all setup scripts in the correct order.'

    def handle(self, *args, **options):
        self.stdout.write(self.style.MIGRATE_LABEL(
            '--- Starting Full System Initialization ---'
        ))

        # Tenant-plane (dormant) permissions + superuser - kept for now.
        management.call_command('setup_permissions')
        management.call_command('setup_superuser')

        # Platform-plane seeds
        management.call_command('seed_features')
        management.call_command('seed_packages')
        management.call_command('seed_platform_rbac')
        management.call_command('bootstrap_platform')

        self.stdout.write(self.style.SUCCESS('--- System Ready ---'))
