from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from apps.core.organizations.models import Organization
from apps.core.crm.services import (
    CompanyService,
    ContactService,
    PipelineService,
    DealService,
)

User = get_user_model()


class Command(BaseCommand):
    help = "Seed CRM demo data"

    def handle(self, *args, **options):
        admin = User.objects.filter(is_superuser=True).first()
        if not admin:
            self.stdout.write(self.style.WARNING("No superuser found."))
            return

        org = Organization.objects.first()
        if not org:
            self.stdout.write(
                self.style.WARNING(
                    "No organization found. Run seed_organizations first."
                )
            )
            return

        org_id = str(org.id)

        # Create a pipeline
        pipeline = PipelineService.create(
            {
                "name": "Default Sales Pipeline",
                "stages": [
                    "Lead",
                    "Qualified",
                    "Proposal",
                    "Negotiation",
                    "Won",
                    "Lost",
                ],
                "organization_id": org_id,  # ← required
            }
        )
        self.stdout.write(f"Pipeline created: {pipeline.name}")

        # Create a company
        company = CompanyService.create(
            {
                "name": "Acme Corp",
                "website": "https://acme.example.com",
                "industry": "Technology",
                "organization_id": org_id,  # ← required
            }
        )
        self.stdout.write(f"Company created: {company.name}")

        # Create a contact
        contact = ContactService.create(
            {
                "first_name": "John",
                "last_name": "Doe",
                "email": "john@acme.example.com",
                "company_id": str(company.id),
                "organization_id": org_id,  # ← required
            }
        )
        self.stdout.write(f"Contact created: {contact.get_full_name()}")

        # Create a deal
        DealService.create(
            {
                "title": "Enterprise Software License",
                "pipeline_id": str(pipeline.id),
                "stage": "Proposal",
                "contact_id": str(contact.id),
                "company_id": str(company.id),
                "amount": "5000.00",
                "expected_close_date": "2025-12-31",
                "organization_id": org_id,  # ← required
            }
        )
        self.stdout.write("Deal created.")
        self.stdout.write(self.style.SUCCESS("CRM seeding completed."))
