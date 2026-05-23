from typing import List, Dict, Optional
from .models import Organization, OrganizationMembership


class OrganizationSelector:
    @staticmethod
    def list_for_user(user) -> List[Dict]:
        memberships = OrganizationMembership.objects.filter(user=user).select_related(
            "organization", "role"
        )
        return [
            {
                "id": str(m.organization.id),
                "name": m.organization.name,
                "slug": m.organization.slug,
                "is_active": m.organization.is_active,
                "role": m.role.display_name if m.role else None,
            }
            for m in memberships
        ]

    @staticmethod
    def get_detail(org_id: str) -> Optional[Dict]:
        try:
            org = Organization.objects.get(pk=org_id)
            return {
                "id": str(org.id),
                "name": org.name,
                "slug": org.slug,
                "is_active": org.is_active,
                "created_at": org.created_at.isoformat(),
            }
        except Organization.DoesNotExist:
            return None

    @staticmethod
    def list_all() -> List[Dict]:
        orgs = Organization.objects.all()
        return [
            {
                "id": str(org.id),
                "name": org.name,
                "slug": org.slug,
                "is_active": org.is_active,
            }
            for org in orgs
        ]

    @staticmethod
    def get_org_instance(org_id: str) -> Optional[Organization]:
        try:
            return Organization.objects.get(pk=org_id)
        except Organization.DoesNotExist:
            return None
