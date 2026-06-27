"""Read‑only queries for the Contact model."""

from typing import List, Dict, Optional
from ..models import Contact


class ContactSelector:
    @staticmethod
    def list_all() -> List[Dict]:
        contacts = Contact.objects.select_related("company").all()
        return [
            {
                "id": str(c.id),
                "first_name": c.first_name,
                "last_name": c.last_name,
                "full_name": c.get_full_name(),
                "email": c.email,
                "phone": c.phone,
                "job_title": c.job_title,
                "company_id": str(c.company.id) if c.company else None,
                "company_name": c.company.name if c.company else None,
                "is_active": c.is_active,
            }
            for c in contacts
        ]

    @staticmethod
    def get_detail(contact_id: str) -> Optional[Dict]:
        try:
            c = Contact.objects.select_related("company").get(pk=contact_id)
            return {
                "id": str(c.id),
                "first_name": c.first_name,
                "last_name": c.last_name,
                "full_name": c.get_full_name(),
                "email": c.email,
                "phone": c.phone,
                "job_title": c.job_title,
                "company_id": str(c.company.id) if c.company else None,
                "company_name": c.company.name if c.company else None,
                "is_active": c.is_active,
            }
        except Contact.DoesNotExist:
            return None
