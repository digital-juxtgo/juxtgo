"""
Contact model – represents a person associated with a company (or standalone).
Each contact belongs to exactly one tenant organization.
"""

from django.db import models
from apps.core.shared.models import BaseModel
from apps.core.shared.managers import TenantManager
from apps.core.tenancy.mixins import TenantQuerysetMixin


class Contact(BaseModel, TenantQuerysetMixin):
    """
    A person (contact) belonging to a tenant organization.
    Optionally linked to a company.
    """

    organization = models.ForeignKey(
        "organizations.Organization",
        on_delete=models.CASCADE,
        related_name="crm_contacts",
        help_text="Tenant organization this contact belongs to",
    )
    company = models.ForeignKey(
        "crm.Company",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="contacts",
        help_text="Optional company this contact works for",
    )
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    email = models.EmailField(blank=True, help_text="Email address (optional)")
    phone = models.CharField(
        max_length=50, blank=True, help_text="Phone number (optional)"
    )
    job_title = models.CharField(
        max_length=100, blank=True, help_text="Job title (optional)"
    )
    is_active = models.BooleanField(
        default=True, help_text="Whether the contact is currently active"
    )

    objects = TenantManager()

    class Meta:
        db_table = "crm_contact"
        ordering = ["last_name", "first_name"]
        verbose_name = "contact"
        verbose_name_plural = "contacts"

    def __str__(self):
        return f"{self.first_name} {self.last_name}"

    def get_full_name(self):
        """Return the contact’s full name."""
        return f"{self.first_name} {self.last_name}"
