from django.test import TestCase, RequestFactory
from django.contrib.sessions.middleware import SessionMiddleware
from django.contrib.auth import get_user_model
from apps.core.organizations.models import Organization
from apps.core.tenancy.middleware import TenancyMiddleware
from apps.core.tenancy.middleware import get_current_org_id
from apps.core.shared.managers import TenantManager

User = get_user_model()


class TenancyMiddlewareTests(TestCase):
    def setUp(self):
        self.factory = RequestFactory()
        self.user = User.objects.create_user(email="tenancy@test.com", password="pass")
        self.org = Organization.objects.create(name="Tenant Org", slug="tenant-org")

    def _apply_middleware(self, request):
        """Helper to apply session and tenancy middleware to a request."""
        session_mw = SessionMiddleware(get_response=lambda r: None)
        session_mw.process_request(request)
        request.session.save()
        tenancy_mw = TenancyMiddleware(get_response=lambda r: None)
        tenancy_mw(request)

    def test_middleware_sets_org_id(self):
        request = self.factory.get("/")
        request.user = self.user
        self._apply_middleware(request)
        request.session["current_org_id"] = str(self.org.id)
        request.session.save()
        # Re‑apply middleware to pick up the session change
        TenancyMiddleware(get_response=lambda r: None)(request)
        self.assertEqual(get_current_org_id(), str(self.org.id))

    def test_middleware_none_when_no_session(self):
        request = self.factory.get("/")
        request.user = self.user
        self._apply_middleware(request)
        self.assertIsNone(get_current_org_id())
