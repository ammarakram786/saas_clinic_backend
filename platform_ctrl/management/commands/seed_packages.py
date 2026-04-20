from decimal import Decimal

from django.core.management.base import BaseCommand
from django.db import transaction

from platform_ctrl.models import Feature, Package, PackageFeature


PACKAGES = [
    {
        'code': 'starter',
        'name': 'Starter',
        'description': 'For single-practitioner clinics just getting started.',
        'currency': 'USD',
        'price_monthly': Decimal('29.00'),
        'price_yearly': Decimal('290.00'),
        'is_public': True,
        'sort_order': 10,
        'features': {
            'appointments': 200,
            'patients': 500,
            'billing': None,
            'email_reminders': 1000,
            'reports': 5,
        },
    },
    {
        'code': 'pro',
        'name': 'Pro',
        'description': 'For multi-practitioner clinics with higher volumes.',
        'currency': 'USD',
        'price_monthly': Decimal('89.00'),
        'price_yearly': Decimal('890.00'),
        'is_public': True,
        'sort_order': 20,
        'features': {
            'appointments': 2000,
            'patients': 5000,
            'billing': None,
            'insurance': None,
            'email_reminders': 10000,
            'sms_reminders': 1000,
            'reports': None,
            'api_access': None,
        },
    },
    {
        'code': 'enterprise',
        'name': 'Enterprise',
        'description': 'Unlimited usage, multi-branch, premium support.',
        'currency': 'USD',
        'price_monthly': None,
        'price_yearly': None,
        'is_public': False,
        'sort_order': 30,
        'features': {
            'appointments': None,
            'patients': None,
            'billing': None,
            'insurance': None,
            'email_reminders': None,
            'sms_reminders': None,
            'reports': None,
            'multi_branch': None,
            'api_access': None,
            'custom_branding': None,
        },
    },
]


class Command(BaseCommand):
    help = 'Seed Starter / Pro / Enterprise packages. Idempotent.'

    @transaction.atomic
    def handle(self, *args, **options):
        if not Feature.objects.exists():
            self.stdout.write(self.style.WARNING(
                'No features found. Run `seed_features` first.'
            ))
            return

        features_by_code = {f.code: f for f in Feature.objects.all()}

        for spec in PACKAGES:
            feature_map = spec.pop('features')
            package, _ = Package.objects.update_or_create(
                code=spec['code'],
                defaults={k: v for k, v in spec.items() if k != 'code'},
            )

            PackageFeature.objects.filter(package=package).delete()
            rows = []
            for code, limit in feature_map.items():
                feature = features_by_code.get(code)
                if feature is None:
                    self.stdout.write(self.style.WARNING(
                        f'Skipping missing feature `{code}` for package `{package.code}`.'
                    ))
                    continue
                rows.append(PackageFeature(
                    package=package, feature=feature, limit_value=limit,
                ))
            PackageFeature.objects.bulk_create(rows)

            self.stdout.write(self.style.SUCCESS(
                f'Seeded package `{package.code}` with {len(rows)} features.'
            ))
