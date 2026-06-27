"""
Deal model – represents a deal (opportunity) moving through a sales pipeline.
Each deal belongs to exactly one tenant organization.
"""

from django.db import models
from apps.core.shared.models import BaseModel
from apps.core.shared.managers import TenantManager
from apps.core.tenancy.mixins import TenantQuerysetMixin


class Deal(BaseModel, TenantQuerysetMixin):
    """
    A deal (opportunity) tracked in a sales pipeline.
    """

    organization = models.ForeignKey(
        "organizations.Organization",
        on_delete=models.CASCADE,
        related_name="crm_deals",
        help_text="Tenant organization this deal belongs to",
    )
    pipeline = models.ForeignKey(
        "crm.Pipeline",
        on_delete=models.CASCADE,
        related_name="deals",
        help_text="Pipeline this deal is part of",
    )
    stage = models.CharField(
        max_length=100,
        help_text="Current stage name (must match one of pipeline’s stages)",
    )
    contact = models.ForeignKey(
        "crm.Contact",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="deals",
        help_text="Primary contact for this deal (optional)",
    )
    company = models.ForeignKey(
        "crm.Company",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="deals",
        help_text="Company linked to this deal (optional)",
    )
    title = models.CharField(max_length=200)
    amount = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        null=True,
        blank=True,
        help_text="Deal amount in currency (optional)",
    )
    expected_close_date = models.DateField(
        null=True, blank=True, help_text="Expected close date (optional)"
    )
    is_won = models.BooleanField(
        default=False, help_text="Whether the deal has been won"
    )
    is_lost = models.BooleanField(
        default=False, help_text="Whether the deal has been lost"
    )

    objects = TenantManager()

    class Meta:
        db_table = "crm_deal"
        ordering = ["-created_at"]
        verbose_name = "deal"
        verbose_name_plural = "deals"

    def __str__(self):
        return self.title
