from django.core.management.base import BaseCommand
from apps.core.permissions.services.role_service import RoleService
from apps.core.permissions.selectors.role_selector import RoleSelector


class Command(BaseCommand):
    help = "Seed roles: admin, manager, support"

    def handle(self, *args, **options):
        roles_data = [
            {"name": "admin", "display_name": "Admin", "description": "Full access"},
            {
                "name": "manager",
                "display_name": "Manager",
                "description": "Manage users",
            },
            {
                "name": "support",
                "display_name": "Support",
                "description": "Customer support",
            },
        ]
        existing = [r["name"] for r in RoleSelector.list_roles()]
        for data in roles_data:
            if data["name"] not in existing:
                RoleService.create_role(**data)
                self.stdout.write(f"Created role: {data['name']}")
            else:
                self.stdout.write(f"Role exists: {data['name']}")
        self.stdout.write(self.style.SUCCESS("Roles seeding completed."))
