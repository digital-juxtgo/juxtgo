"""Read‑only queries for the Deal model."""

from typing import List, Dict, Optional
from ..models import Deal


class DealSelector:
    @staticmethod
    def list_all() -> List[Dict]:
        deals = Deal.objects.select_related("pipeline", "contact", "company").all()
        return [
            {
                "id": str(d.id),
                "title": d.title,
                "pipeline_name": d.pipeline.name,
                "stage": d.stage,
                "contact_name": d.contact.get_full_name() if d.contact else None,
                "company_name": d.company.name if d.company else None,
                "amount": str(d.amount) if d.amount else None,
                "expected_close_date": (
                    d.expected_close_date.isoformat() if d.expected_close_date else None
                ),
                "is_won": d.is_won,
                "is_lost": d.is_lost,
            }
            for d in deals
        ]

    @staticmethod
    def get_detail(deal_id: str) -> Optional[Dict]:
        try:
            d = Deal.objects.select_related("pipeline", "contact", "company").get(
                pk=deal_id
            )
            return {
                "id": str(d.id),
                "title": d.title,
                "pipeline_id": str(d.pipeline.id),
                "stage": d.stage,
                "contact_id": str(d.contact.id) if d.contact else None,
                "company_id": str(d.company.id) if d.company else None,
                "amount": str(d.amount) if d.amount else None,
                "expected_close_date": (
                    d.expected_close_date.isoformat() if d.expected_close_date else None
                ),
                "is_won": d.is_won,
                "is_lost": d.is_lost,
            }
        except Deal.DoesNotExist:
            return None
