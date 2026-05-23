from django.test import TestCase

# Create your tests here.
from django.test import TestCase
from django.contrib.auth import get_user_model
from .models import Organization, OrganizationMembership
from .selectors import OrganizationSelector
from .services import OrganizationService

User = get_user_model()


class OrganizationServiceTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            email="orgtest@example.com", password="testpass123"
        )

    def test_create_organization_with_owner(self):
        org = OrganizationService.create_organization("Test Org", self.user)
        self.assertEqual(org.name, "Test Org")
        self.assertTrue(
            OrganizationMembership.objects.filter(
                user=self.user, organization=org, role__name="owner"
            ).exists()
        )

    def test_switch_organization_valid_membership(self):
        org = OrganizationService.create_organization("Switch Org", self.user)
        org2 = OrganizationService.switch_organization(self.user, org.id)
        self.assertEqual(org, org2)

    def test_switch_organization_no_membership_raises(self):
        other_org = OrganizationService.create_organization("Other Org", self.user)
        outsider = User.objects.create_user(
            email="outsider@example.com", password="testpass123"
        )
        with self.assertRaises(ValueError):
            OrganizationService.switch_organization(outsider, other_org.id)


class OrganizationSelectorTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            email="selorg@example.com", password="testpass123"
        )
        self.org = OrganizationService.create_organization("Sel Org", self.user)

    def test_list_for_user_returns_dicts(self):
        orgs = OrganizationSelector.list_for_user(self.user)
        self.assertEqual(len(orgs), 1)
        self.assertEqual(orgs[0]["name"], "Sel Org")
        self.assertEqual(orgs[0]["role"], "Owner")
