from django.core.management.base import BaseCommand
from django.db import transaction

from control.models import Feature


FEATURES = [
    {'code': 'appointments',      'name': 'Appointments',        'category': 'clinical'},
    {'code': 'patients',          'name': 'Patient Records',     'category': 'clinical'},
    {'code': 'billing',           'name': 'Billing',             'category': 'finance'},
    {'code': 'insurance',         'name': 'Insurance Claims',    'category': 'finance'},
    {'code': 'sms_reminders',     'name': 'SMS Reminders',       'category': 'communication'},
    {'code': 'email_reminders',   'name': 'Email Reminders',     'category': 'communication'},
    {'code': 'reports',           'name': 'Reports & Analytics', 'category': 'analytics'},
    {'code': 'multi_branch',      'name': 'Multi-Branch',        'category': 'platform'},
    {'code': 'api_access',        'name': 'API Access',          'category': 'platform'},
    {'code': 'custom_branding',   'name': 'Custom Branding',     'category': 'platform'},
]


class Command(BaseCommand):
    help = 'Seed the global feature catalog. Idempotent.'

    @transaction.atomic
    def handle(self, *args, **options):
        self.stdout.write('Syncing features...')
        created = updated = 0
        codes = []
        for item in FEATURES:
            obj, was_created = Feature.objects.update_or_create(
                code=item['code'],
                defaults={
                    'name': item['name'],
                    'category': item.get('category', ''),
                    'description': item.get('description', ''),
                    'is_active': True,
                },
            )
            codes.append(obj.code)
            if was_created:
                created += 1
            else:
                updated += 1

        self.stdout.write(self.style.SUCCESS(
            f'Features synced. Created={created} Updated={updated}'
        ))
