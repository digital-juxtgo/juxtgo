"""Read‑only queries for the Company model – return dicts only."""

from typing import List, Dict, Optional
from ..models import Company


class CompanySelector:
    @staticmethod
    def list_all() -> List[Dict]:
        companies = Company.objects.all()
        return [
            {
                "id": str(c.id),
                "name": c.name,
                "website": c.website,
                "industry": c.industry,
                "is_active": c.is_active,
            }
            for c in companies
        ]

    @staticmethod
    def get_detail(company_id: str) -> Optional[Dict]:
        try:
            c = Company.objects.get(pk=company_id)
            return {
                "id": str(c.id),
                "name": c.name,
                "website": c.website,
                "industry": c.industry,
                "is_active": c.is_active,
            }
        except Company.DoesNotExist:
            return None
