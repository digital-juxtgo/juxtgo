"""
Company model – represents an organization’s corporate client or partner.
Each company belongs to exactly one tenant organization.
"""

from django.db import models
from apps.core.shared.models import BaseModel
from apps.core.shared.managers import TenantManager
from apps.core.tenancy.mixins import TenantQuerysetMixin


class Company(BaseModel, TenantQuerysetMixin):
    """
    A company (B2B client) belonging to a tenant organization.
    """

    organization = models.ForeignKey(
        "organizations.Organization",
        on_delete=models.CASCADE,
        related_name="crm_companies",
        help_text="Tenant organization this company belongs to",
    )
    name = models.CharField(max_length=200)
    website = models.URLField(blank=True, help_text="Optional company website")
    industry = models.CharField(
        max_length=100, blank=True, help_text="e.g. Technology, Healthcare"
    )
    is_active = models.BooleanField(
        default=True, help_text="Whether the company is currently active"
    )

    # TenantManager automatically filters querysets by the current organization
    objects = TenantManager()

    class Meta:
        db_table = "crm_company"
        ordering = ["name"]
        verbose_name = "company"
        verbose_name_plural = "companies"

    def __str__(self):
        return self.name
