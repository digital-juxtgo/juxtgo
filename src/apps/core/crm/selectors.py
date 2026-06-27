from typing import List, Dict, Optional
from .models import Company, Contact, Pipeline, Deal


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


class PipelineSelector:
    @staticmethod
    def list_all() -> List[Dict]:
        pipelines = Pipeline.objects.all()
        return [
            {
                "id": str(p.id),
                "name": p.name,
                "stages": p.stages,
                "is_active": p.is_active,
            }
            for p in pipelines
        ]

    @staticmethod
    def get_detail(pipeline_id: str) -> Optional[Dict]:
        try:
            p = Pipeline.objects.get(pk=pipeline_id)
            return {
                "id": str(p.id),
                "name": p.name,
                "stages": p.stages,
                "is_active": p.is_active,
            }
        except Pipeline.DoesNotExist:
            return None


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
