"""Write operations for Company."""

import logging
from ..models import Company

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
