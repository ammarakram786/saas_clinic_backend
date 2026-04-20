from django.core.management.base import BaseCommand
from django.db import transaction

from platform_ctrl.models import PlatformPermission, PlatformRole


PERMISSIONS = [
    # (code_name, name, module, description)
    ('platform.tenant.read',            'Read Tenants',            'tenant',        'View tenant list and details.'),
    ('platform.tenant.create',          'Create Tenants',          'tenant',        'Onboard new tenants.'),
    ('platform.tenant.update',          'Update Tenants',          'tenant',        'Edit tenant fields.'),
    ('platform.tenant.suspend',         'Suspend Tenants',         'tenant',        'Suspend an active tenant.'),
    ('platform.tenant.activate',        'Activate Tenants',        'tenant',        'Activate a suspended/trial tenant.'),
    ('platform.tenant.cancel',          'Cancel Tenants',          'tenant',        'Cancel a tenant (soft).'),

    ('platform.package.read',           'Read Packages',           'package',       'View packages.'),
    ('platform.package.manage',         'Manage Packages',         'package',       'Create/edit/delete packages.'),

    ('platform.feature.read',           'Read Features',           'feature',       'View feature catalog.'),
    ('platform.feature.manage',         'Manage Features',         'feature',       'Create/edit/deactivate features.'),

    ('platform.subscription.read',      'Read Subscriptions',      'subscription',  'View tenant subscriptions.'),
    ('platform.subscription.assign',    'Assign Packages',         'subscription',  'Assign/change a tenant package.'),

    ('platform.override.read',          'Read Overrides',          'override',      'View tenant feature overrides.'),
    ('platform.override.manage',        'Manage Overrides',        'override',      'Upsert/remove overrides.'),

    ('platform.audit.read',             'Read Audit Log',          'audit',         'View the platform audit log.'),

    ('platform.platform_user.read',     'Read Platform Users',     'platform_user', 'View platform users.'),
    ('platform.platform_user.manage',   'Manage Platform Users',   'platform_user', 'Create/edit platform users.'),
    ('platform.platform_role.read',     'Read Platform Roles',     'platform_user', 'View platform roles.'),
    ('platform.platform_role.manage',   'Manage Platform Roles',   'platform_user', 'Create/edit platform roles.'),
]

# code_name -> list[permission.code_name]; '*' means "every permission"
ROLES = {
    'platform_super_admin': {
        'name': 'Platform Super Admin',
        'description': 'Full access to everything on the control plane.',
        'permissions': '*',
    },
    'platform_support': {
        'name': 'Platform Support',
        'description': 'Read-most + tenant lifecycle for customer support.',
        'permissions': [
            'platform.tenant.read', 'platform.tenant.update',
            'platform.tenant.suspend', 'platform.tenant.activate',
            'platform.package.read',
            'platform.feature.read',
            'platform.subscription.read',
            'platform.override.read', 'platform.override.manage',
            'platform.audit.read',
        ],
    },
    'platform_billing': {
        'name': 'Platform Billing',
        'description': 'Can manage packages and subscriptions; read-only on tenants.',
        'permissions': [
            'platform.tenant.read',
            'platform.package.read', 'platform.package.manage',
            'platform.feature.read',
            'platform.subscription.read', 'platform.subscription.assign',
            'platform.audit.read',
        ],
    },
    'platform_read_only': {
        'name': 'Platform Read Only',
        'description': 'View-only access across the control plane.',
        'permissions': [
            'platform.tenant.read',
            'platform.package.read',
            'platform.feature.read',
            'platform.subscription.read',
            'platform.override.read',
            'platform.audit.read',
            'platform.platform_user.read',
            'platform.platform_role.read',
        ],
    },
}


class Command(BaseCommand):
    help = 'Seed platform RBAC: permissions + four default roles. Idempotent.'

    @transaction.atomic
    def handle(self, *args, **options):
        self.stdout.write('Seeding platform permissions...')
        for code, name, module, desc in PERMISSIONS:
            PlatformPermission.objects.update_or_create(
                code_name=code,
                defaults={'name': name, 'module': module, 'description': desc},
            )

        PlatformPermission.objects.exclude(
            code_name__in=[p[0] for p in PERMISSIONS],
        ).delete()

        all_perms = {p.code_name: p for p in PlatformPermission.objects.all()}

        for code_name, spec in ROLES.items():
            role, _ = PlatformRole.objects.update_or_create(
                code_name=code_name,
                defaults={
                    'name': spec['name'],
                    'description': spec['description'],
                },
            )
            if spec['permissions'] == '*':
                role.permissions.set(all_perms.values())
            else:
                role.permissions.set([all_perms[c] for c in spec['permissions']])

        self.stdout.write(self.style.SUCCESS(
            f'Platform RBAC synced: {len(PERMISSIONS)} permissions, {len(ROLES)} roles.'
        ))
