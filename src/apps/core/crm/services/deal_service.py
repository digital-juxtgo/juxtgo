"""Write operations for Deal."""

import logging
from ..models import Deal

logger = logging.getLogger(__name__)


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
