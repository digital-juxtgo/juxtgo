import logging
from django.db import transaction
from .models import Company, Contact, Pipeline, Deal

logger = logging.getLogger(__name__)


class CompanyService:
    @staticmethod
    def create(data: dict) -> Company:
        company = Company.objects.create(**data)
        logger.info("Company created: %s", company.name)
        return company

    @staticmethod
    def update(company_id: str, data: dict) -> Company:
        company = Company.objects.get(pk=company_id)
        for field, value in data.items():
            setattr(company, field, value)
        company.save()
        logger.info("Company updated: %s", company.name)
        return company

    @staticmethod
    def delete(company_id: str) -> None:
        company = Company.objects.get(pk=company_id)
        company.delete()
        logger.info("Company deleted: %s", company.name)


class ContactService:
    @staticmethod
    def create(data: dict) -> Contact:
        contact = Contact.objects.create(**data)
        logger.info("Contact created: %s", contact.get_full_name())
        return contact

    @staticmethod
    def update(contact_id: str, data: dict) -> Contact:
        contact = Contact.objects.get(pk=contact_id)
        for field, value in data.items():
            setattr(contact, field, value)
        contact.save()
        logger.info("Contact updated: %s", contact.get_full_name())
        return contact

    @staticmethod
    def delete(contact_id: str) -> None:
        contact = Contact.objects.get(pk=contact_id)
        contact.delete()
        logger.info("Contact deleted: %s", contact.get_full_name())


class PipelineService:
    @staticmethod
    def create(data: dict) -> Pipeline:
        pipeline = Pipeline.objects.create(**data)
        logger.info("Pipeline created: %s", pipeline.name)
        return pipeline

    @staticmethod
    def update(pipeline_id: str, data: dict) -> Pipeline:
        pipeline = Pipeline.objects.get(pk=pipeline_id)
        for field, value in data.items():
            setattr(pipeline, field, value)
        pipeline.save()
        logger.info("Pipeline updated: %s", pipeline.name)
        return pipeline

    @staticmethod
    def delete(pipeline_id: str) -> None:
        pipeline = Pipeline.objects.get(pk=pipeline_id)
        pipeline.delete()
        logger.info("Pipeline deleted: %s", pipeline.name)


class DealService:
    @staticmethod
    def create(data: dict) -> Deal:
        deal = Deal.objects.create(**data)
        logger.info("Deal created: %s", deal.title)
        return deal

    @staticmethod
    def update(deal_id: str, data: dict) -> Deal:
        deal = Deal.objects.get(pk=deal_id)
        for field, value in data.items():
            setattr(deal, field, value)
        deal.save()
        logger.info("Deal updated: %s", deal.title)
        return deal

    @staticmethod
    def delete(deal_id: str) -> None:
        deal = Deal.objects.get(pk=deal_id)
        deal.delete()
        logger.info("Deal deleted: %s", deal.title)
