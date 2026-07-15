from django.contrib.auth.models import Group, Permission
from django.core.management.base import BaseCommand, CommandError

from core.authorization.roles import ROLE_PERMISSIONS


class Command(BaseCommand):
    help = "Create or update the application's RBAC groups and permissions."

    def handle(self, *args, **options):
        available_permissions = {
            (
                f"{permission.content_type.app_label}."
                f"{permission.codename}"
            ): permission
            for permission in Permission.objects.select_related("content_type")
        }

        required_permissions = {
            permission_name
            for role_permissions in ROLE_PERMISSIONS.values()
            for permission_name in role_permissions
        }

        missing_permissions = (
            required_permissions - available_permissions.keys()
        )

        if missing_permissions:
            formatted_permissions = "\n".join(
                f"  - {permission_name}"
                for permission_name in sorted(missing_permissions)
            )

            raise CommandError(
                "The following permissions do not exist:\n"
                f"{formatted_permissions}\n\n"
                "Run migrations before running setup_rbac."
            )

        for role_name, permission_names in ROLE_PERMISSIONS.items():
            group, created = Group.objects.get_or_create(name=role_name)

            permissions = [
                available_permissions[permission_name]
                for permission_name in sorted(permission_names)
            ]

            group.permissions.set(permissions)

            action = "Created" if created else "Updated"

            self.stdout.write(
                self.style.SUCCESS(
                    f"{action} role '{role_name}' "
                    f"with {len(permissions)} permissions."
                )
            )

        self.stdout.write(
            self.style.SUCCESS("RBAC role setup completed.")
        )
