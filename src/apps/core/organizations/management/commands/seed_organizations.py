from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand

from apps.core.organizations.services import OrganizationService

User = get_user_model()


class Command(BaseCommand):
    help = "Seed demo organizations for the first superuser."

    def handle(self, *args, **options):
        superuser = User.objects.filter(is_superuser=True).first()
        if not superuser:
            self.stdout.write(
                self.style.WARNING("No superuser found; skipping organisation seed.")
            )
            return

        demo_names = ["JuxtGo Digital", "JuxtGo Mart", "Acme Corp"]
        for name in demo_names:
            try:
                org = OrganizationService.create_organization(
                    name=name, creator_user=superuser
                )
                self.stdout.write(
                    self.style.SUCCESS(f"Created organization: {org.name} ({org.slug})")
                )
            except Exception as e:
                self.stdout.write(self.style.ERROR(f"Failed to create {name}: {e}"))
