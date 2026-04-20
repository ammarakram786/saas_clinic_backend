from django.core.management.base import BaseCommand
from account.models import Permission


class Command(BaseCommand):
    help = 'Seeds the database with required system permissions'

    def handle(self, *args, **options):
        # Using a list of dictionaries makes the data easier to manage
        permissions_data = [
            # account Permissions
            Permission(name='Create User', code_name='create_user', module_name='User',
                       description='User can create user'),
            Permission(name='Read User', code_name='read_user', module_name='User',
                       description='User can read user'),
            Permission(name='Update User', code_name='update_user', module_name='User',
                       description='User can update user'),
            Permission(name='Delete User', code_name='delete_user', module_name='User',
                       description='User can delete user'),
            Permission(name='Show User', code_name='show_user', module_name='User',
                       description='User can view user'),

            Permission(name='Create Role', code_name='create_role', module_name='Role',
                       description='User can create role'),
            Permission(name='Read Role', code_name='read_role', module_name='Role',
                       description='User can read role'),
            Permission(name='Update Role', code_name='update_role', module_name='Role',
                       description='User can update role'),
            Permission(name='Delete Role', code_name='delete_role', module_name='Role',
                       description='User can delete role'),
            Permission(name='Show Role', code_name='show_role', module_name='Role',
                       description='User can view role'),

        ]

        self.stdout.write(self.style.NOTICE('Syncing permissions to database...'))

        created_count = 0
        updated_count = 0
        code_names = []

        for item in permissions_data:
            obj, created = Permission.objects.update_or_create(
                code_name=item.code_name,  # Changed from item['code_name']
                defaults={
                    'name': item.name,
                    'module_name': item.module_name,
                    'description': item.description
                }
            )
            code_names.append(item.code_name)
            if created:
                created_count += 1
            else:
                updated_count += 1

        deleted_count, _ = Permission.objects.exclude(code_name__in=code_names).delete()

        self.stdout.write(self.style.SUCCESS(
            f'Successfully synced permissions! (Created: {created_count}, Updated: {updated_count}, Deleted: {deleted_count})'
        ))