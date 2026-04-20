import os
import secrets
import string

from django.core.management.base import BaseCommand
from django.db import transaction

from platform_ctrl.models import PlatformRole, PlatformUser


def _generate_password(length: int = 24) -> str:
    alphabet = string.ascii_letters + string.digits + '-_'
    return ''.join(secrets.choice(alphabet) for _ in range(length))


class Command(BaseCommand):
    help = 'Bootstrap a platform super-admin user. Idempotent.'

    @transaction.atomic
    def handle(self, *args, **options):
        try:
            role = PlatformRole.objects.get(code_name='platform_super_admin')
        except PlatformRole.DoesNotExist:
            self.stdout.write(self.style.ERROR(
                "`platform_super_admin` role not found. Run `seed_platform_rbac` first."
            ))
            return

        email = os.environ.get('PLATFORM_BOOTSTRAP_EMAIL', 'admin@local').strip().lower()
        password_env = os.environ.get('PLATFORM_BOOTSTRAP_PASSWORD', '').strip()

        user = PlatformUser.objects.filter(email=email).first()
        if user is None:
            password = password_env or _generate_password()
            user = PlatformUser.objects.create_user(
                email=email,
                password=password,
                full_name='Platform Admin',
                is_active=True,
            )
            user.role = role
            user.save(update_fields=['role'])

            self.stdout.write(self.style.SUCCESS(
                f'Created platform super-admin `{email}`.'
            ))
            if not password_env:
                self.stdout.write(self.style.WARNING(
                    f'Generated password (save it now): {password}'
                ))
        else:
            if user.role_id != role.pk:
                user.role = role
                user.save(update_fields=['role'])
            self.stdout.write(self.style.NOTICE(
                f'Platform user `{email}` already exists. Role ensured.'
            ))
