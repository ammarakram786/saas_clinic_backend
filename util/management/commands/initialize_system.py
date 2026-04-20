from django.core import management
from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = 'Runs all setup scripts in the correct order'

    def handle(self, *args, **options):
        self.stdout.write(self.style.MIGRATE_LABEL("--- Starting Full System Initialization ---"))

        # Call other commands programmatically
        management.call_command('setup_permissions')
        management.call_command('setup_superuser')


        self.stdout.write(self.style.SUCCESS("--- System Ready ---"))