from django.test import TestCase
from django.contrib.auth import get_user_model
from apps.core.organizations.models import Organization
from .models import Company, Contact, Pipeline, Deal
from .selectors import CompanySelector, ContactSelector, PipelineSelector, DealSelector
from .services import CompanyService, ContactService, PipelineService, DealService
from apps.core.tenancy.middleware import _thread_locals

User = get_user_model()


class CRMTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_superuser(
            email="crmtest@example.com", password="pass"
        )
        self.org = Organization.objects.create(name="Test Org", slug="test-org")
        self.org_id = str(self.org.id)

        # Simulate what the TenancyMiddleware does during a request
        _thread_locals.org_id = self.org_id

    def tearDown(self):
        _thread_locals.org_id = None

    def test_create_company(self):
        company = CompanyService.create(
            {
                "name": "Acme",
                "website": "https://a.com",
                "industry": "Tech",
                "organization_id": self.org_id,
            }
        )
        self.assertEqual(company.name, "Acme")
        companies = CompanySelector.list_all()
        self.assertEqual(len(companies), 1)

    def test_create_contact(self):
        company = CompanyService.create(
            {"name": "Acme", "organization_id": self.org_id}
        )
        contact = ContactService.create(
            {
                "first_name": "Jane",
                "last_name": "Doe",
                "email": "j@a.com",
                "company_id": str(company.id),
                "organization_id": self.org_id,
            }
        )
        self.assertEqual(contact.get_full_name(), "Jane Doe")
        contacts = ContactSelector.list_all()
        self.assertEqual(len(contacts), 1)

    def test_create_pipeline(self):
        pipeline = PipelineService.create(
            {
                "name": "Sales",
                "stages": ["Lead", "Won"],
                "organization_id": self.org_id,
            }
        )
        self.assertEqual(pipeline.name, "Sales")
        pipelines = PipelineSelector.list_all()
        self.assertEqual(len(pipelines), 1)

    def test_create_deal(self):
        pipeline = PipelineService.create(
            {
                "name": "Sales",
                "stages": ["Lead", "Won"],
                "organization_id": self.org_id,
            }
        )
        deal = DealService.create(
            {
                "title": "Big Deal",
                "pipeline_id": str(pipeline.id),
                "stage": "Lead",
                "organization_id": self.org_id,
            }
        )
        self.assertEqual(deal.title, "Big Deal")
        deals = DealSelector.list_all()
        self.assertEqual(len(deals), 1)
