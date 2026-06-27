"""Write operations for Contact."""

import logging
from ..models import Contact

logger = logging.getLogger(__name__)


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
