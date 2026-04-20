from django.core.management.base import BaseCommand
from account.models import User, Role, Permission


class Command(BaseCommand):
    help = 'Creates a SuperUser role, assigns all permissions, and creates a default superuser'

    def handle(self, *args, **options):
        self.stdout.write("Populating system roles and superuser...")

        # 1. Get all current permissions
        permissions = Permission.objects.all()
        if not permissions.exists():
            self.stdout.write(self.style.WARNING(
                "No permissions found! Run 'setup_permissions' first."
            ))
            return

        # 2. Setup SuperUser Role
        role, created = Role.objects.get_or_create(
            code_name='su',
            defaults={'name': 'SuperUser'}
        )

        # Clear and re-add to ensure the role has EVERY permission in the DB
        role.permissions.set(permissions)
        role.save()

        status_msg = "Created" if created else "Updated"
        self.stdout.write(self.style.SUCCESS(f"{status_msg} 'su' role with {permissions.count()} permissions."))

        # 3. Setup Default SuperUser
        if not User.objects.filter(username='superuser').exists():
            user = User.objects.create_superuser(
                username="superuser",
                password="123",  # Note: Change this in production!
            )
            user.role = role
            user.save()
            self.stdout.write(self.style.SUCCESS("Created user 'superuser' with password '123'."))
        else:
            # Ensure existing superuser has the correct role
            user = User.objects.get(username='superuser')
            user.role = role
            user.save()
            self.stdout.write(self.style.NOTICE("User 'superuser' already exists. Role updated."))

        self.stdout.write(self.style.SUCCESS("Population complete!"))