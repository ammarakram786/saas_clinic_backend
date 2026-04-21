from django.core.management.base import BaseCommand
from django.db import transaction

from account.models import Permission, Role


PERMISSIONS = [
    ('read_user', 'Read Users', 'user', 'View tenant users.'),
    ('create_user', 'Create Users', 'user', 'Create tenant users.'),
    ('update_user', 'Update Users', 'user', 'Update tenant users.'),
    ('delete_user', 'Delete Users', 'user', 'Deactivate tenant users.'),
    ('read_role', 'Read Roles', 'role', 'View tenant roles.'),
    ('create_role', 'Create Roles', 'role', 'Create tenant roles.'),
    ('update_role', 'Update Roles', 'role', 'Update tenant roles.'),
    ('delete_role', 'Delete Roles', 'role', 'Delete tenant roles.'),
    ('read_profile', 'Read Profiles', 'profile', 'View profiles.'),
    ('create_profile', 'Create Profiles', 'profile', 'Create profiles.'),
    ('update_profile', 'Update Profiles', 'profile', 'Update profiles.'),
    ('delete_profile', 'Delete Profiles', 'profile', 'Delete profiles.'),
]

ROLES = {
    'clinic_admin': {
        'name': 'Clinic Admin',
        'permissions': '*',
    },
    'clinic_staff': {
        'name': 'Clinic Staff',
        'permissions': [
            'read_user',
            'read_role',
            'read_profile',
            'update_profile',
        ],
    },
    'clinic_read_only': {
        'name': 'Clinic Read Only',
        'permissions': [
            'read_user',
            'read_role',
            'read_profile',
        ],
    },
}


class Command(BaseCommand):
    help = 'Seed account RBAC: permissions + baseline tenant-staff roles. Idempotent.'

    @transaction.atomic
    def handle(self, *args, **options):
        self.stdout.write('Seeding account permissions...')
        for code, name, module, desc in PERMISSIONS:
            Permission.objects.update_or_create(
                code_name=code,
                defaults={
                    'name': name,
                    'module_name': module,
                    'description': desc[:50],
                },
            )

        all_perms = {p.code_name: p for p in Permission.objects.all()}

        for code_name, spec in ROLES.items():
            role, _ = Role.objects.update_or_create(
                code_name=code_name,
                defaults={'name': spec['name']},
            )
            if spec['permissions'] == '*':
                role.permissions.set(all_perms.values())
            else:
                role.permissions.set([all_perms[c] for c in spec['permissions']])

        self.stdout.write(self.style.SUCCESS(
            f'Account RBAC synced: {len(PERMISSIONS)} permissions, {len(ROLES)} roles.'
        ))
