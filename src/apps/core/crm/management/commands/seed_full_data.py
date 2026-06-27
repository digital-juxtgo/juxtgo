"""
Management command to seed the entire JuxtGo platform with comprehensive test data.
Covers: organizations, users, CRM (companies, contacts, pipelines, deals).
"""

from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from apps.core.organizations.models import Organization
from apps.core.organizations.services import OrganizationService
from apps.core.permissions.services import RoleService
from apps.core.crm.services import (
    CompanyService,
    ContactService,
    PipelineService,
    DealService,
)

User = get_user_model()


class Command(BaseCommand):
    help = "Seed the full platform with realistic test data"

    def handle(self, *args, **options):
        self.stdout.write("🌱 Seeding JuxtGo OS…")

        # 1. Ensure roles exist
        for role in ["admin", "manager", "support"]:
            RoleService.create_role(role, role.capitalize())

        # 2. Create superuser if not exists
        admin = User.objects.filter(is_superuser=True).first()
        if not admin:
            admin = User.objects.create_superuser(
                email="admin@juxtgo.com",
                password="admin123",
                first_name="Hadi",
                last_name="Admin",
            )
            self.stdout.write(f"✅ Superuser created: {admin.email}")
        else:
            self.stdout.write(f"ℹ️  Superuser exists: {admin.email}")

        # 3. Create a few organizations
        orgs_data = ["JuxtGo Digital", "JuxtGo Mart", "Acme Corp", "Globex Inc"]
        orgs = []
        for name in orgs_data:
            try:
                org = OrganizationService.create_organization(name, admin)
                orgs.append(org)
                self.stdout.write(f"✅ Org created: {org.name}")
            except Exception as e:
                self.stdout.write(f"⚠️  {name}: {e}")

        if not orgs:
            self.stdout.write("❌ No organizations created. Exiting.")
            return

        # Work with the first organization (simulate active tenant)
        org = orgs[0]
        org_id = str(org.id)
        self.stdout.write(f"\n📌 Using organization: {org.name} (ID: {org_id})")

        # 4. Create pipelines
        pipelines = []
        pipeline_defs = [
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
            },
            {
                "name": "Partner Pipeline",
                "stages": ["Applied", "Screening", "Interview", "Approved", "Rejected"],
            },
        ]
        for pdef in pipeline_defs:
            p = PipelineService.create({**pdef, "organization_id": org_id})
            pipelines.append(p)
            self.stdout.write(f"✅ Pipeline: {p.name}")

        # 5. Create companies
        companies_data = [
            {
                "name": "Stark Industries",
                "website": "https://stark.com",
                "industry": "Technology",
            },
            {
                "name": "Wayne Enterprises",
                "website": "https://wayne.com",
                "industry": "Defense",
            },
            {"name": "Oscorp", "website": "https://oscorp.com", "industry": "Biotech"},
            {
                "name": "Umbrella Corp",
                "website": "https://umbrella.com",
                "industry": "Pharma",
            },
            {
                "name": "Cyberdyne Systems",
                "website": "https://cyberdyne.com",
                "industry": "AI & Robotics",
            },
        ]
        companies = []
        for cdata in companies_data:
            c = CompanyService.create({**cdata, "organization_id": org_id})
            companies.append(c)
            self.stdout.write(f"✅ Company: {c.name}")

        # 6. Create contacts (linked to companies)
        contacts_data = [
            {
                "first_name": "Tony",
                "last_name": "Stark",
                "email": "tony@stark.com",
                "phone": "+1-555-0101",
                "job_title": "CEO",
                "company_id": str(companies[0].id),
            },
            {
                "first_name": "Pepper",
                "last_name": "Potts",
                "email": "pepper@stark.com",
                "phone": "+1-555-0102",
                "job_title": "COO",
                "company_id": str(companies[0].id),
            },
            {
                "first_name": "Bruce",
                "last_name": "Wayne",
                "email": "bruce@wayne.com",
                "phone": "+1-555-0201",
                "job_title": "CEO",
                "company_id": str(companies[1].id),
            },
            {
                "first_name": "Norman",
                "last_name": "Osborn",
                "email": "norman@oscorp.com",
                "phone": "+1-555-0301",
                "job_title": "CEO",
                "company_id": str(companies[2].id),
            },
            {
                "first_name": "Alice",
                "last_name": "Rain",
                "email": "alice@umbrella.com",
                "phone": "+1-555-0401",
                "job_title": "Head of Security",
                "company_id": str(companies[3].id),
            },
            {
                "first_name": "Miles",
                "last_name": "Dyson",
                "email": "miles@cyberdyne.com",
                "phone": "+1-555-0501",
                "job_title": "Director",
                "company_id": str(companies[4].id),
            },
            # standalone contact (no company)
            {
                "first_name": "John",
                "last_name": "Doe",
                "email": "john@freelance.com",
                "phone": "+1-555-0001",
                "job_title": "Freelancer",
                "company_id": None,
            },
        ]
        contacts = []
        for cdata in contacts_data:
            c = ContactService.create({**cdata, "organization_id": org_id})
            contacts.append(c)
            self.stdout.write(f"✅ Contact: {c.get_full_name()}")

        # 7. Create deals across pipelines
        deal_defs = [
            {
                "title": "Repulsor Tech License",
                "pipeline_id": str(pipelines[0].id),
                "stage": "Proposal",
                "contact_id": str(contacts[0].id),
                "company_id": str(companies[0].id),
                "amount": "250000.00",
                "expected_close_date": "2025-12-31",
            },
            {
                "title": "Batsuit Supply Contract",
                "pipeline_id": str(pipelines[0].id),
                "stage": "Qualified",
                "contact_id": str(contacts[2].id),
                "company_id": str(companies[1].id),
                "amount": "180000.00",
                "expected_close_date": "2025-10-15",
            },
            {
                "title": "Goblin Glider R&D",
                "pipeline_id": str(pipelines[0].id),
                "stage": "Lead",
                "contact_id": str(contacts[3].id),
                "company_id": str(companies[2].id),
                "amount": "75000.00",
                "expected_close_date": None,
            },
            {
                "title": "T-Virus Antidote Distribution",
                "pipeline_id": str(pipelines[0].id),
                "stage": "Won",
                "contact_id": str(contacts[4].id),
                "company_id": str(companies[3].id),
                "amount": "500000.00",
                "expected_close_date": "2025-03-01",
            },
            {
                "title": "Skynet Prevention Consulting",
                "pipeline_id": str(pipelines[0].id),
                "stage": "Lost",
                "contact_id": str(contacts[5].id),
                "company_id": str(companies[4].id),
                "amount": "100000.00",
                "expected_close_date": "2025-02-01",
            },
            {
                "title": "AI Research Grant",
                "pipeline_id": str(pipelines[1].id),
                "stage": "Applied",
                "contact_id": str(contacts[6].id),
                "company_id": None,
                "amount": "50000.00",
                "expected_close_date": "2025-11-01",
            },
        ]
        for ddef in deal_defs:
            d = DealService.create({**ddef, "organization_id": org_id})
            # Mark won/lost explicitly
            if ddef.get("is_won"):
                d.is_won = True
                d.save(update_fields=["is_won"])
            if ddef.get("is_lost"):
                d.is_lost = True
                d.save(update_fields=["is_lost"])
            self.stdout.write(f"✅ Deal: {d.title} ({d.stage})")

        self.stdout.write(self.style.SUCCESS("\n🎉 Full seed completed!"))
        self.stdout.write(f"   Organizations: {len(orgs)}")
        self.stdout.write(f"   Pipelines:     {len(pipelines)}")
        self.stdout.write(f"   Companies:     {len(companies)}")
        self.stdout.write(f"   Contacts:      {len(contacts)}")
        self.stdout.write(f"   Deals:         {len(deal_defs)}")
