from django.core.management.base import BaseCommand

from control.models import Tenant
from control.services.entitlements import recompute_entitlements


class Command(BaseCommand):
    help = 'Recompute cached entitlement snapshots for every tenant.'

    def add_arguments(self, parser):
        parser.add_argument(
            '--tenant', dest='tenant_slug', default=None,
            help='Recompute only a single tenant (by slug).',
        )

    def handle(self, *args, **options):
        qs = Tenant.objects.all()
        slug = options.get('tenant_slug')
        if slug:
            qs = qs.filter(slug=slug)

        total = qs.count()
        self.stdout.write(f'Recomputing entitlements for {total} tenant(s)...')
        done = 0
        for tenant in qs.iterator():
            recompute_entitlements(tenant)
            done += 1
            if done % 50 == 0:
                self.stdout.write(f'  ... {done}/{total}')

        self.stdout.write(self.style.SUCCESS(f'Done. Recomputed {done} tenant(s).'))
