"""
Pipeline model – represents a sales pipeline with ordered stages.
Each pipeline belongs to exactly one tenant organization.
"""

from django.db import models
from apps.core.shared.models import BaseModel
from apps.core.shared.managers import TenantManager
from apps.core.tenancy.mixins import TenantQuerysetMixin


class Pipeline(BaseModel, TenantQuerysetMixin):
    """
    A sales pipeline (e.g., "Default Sales Pipeline") with a list of stage names.
    """

    organization = models.ForeignKey(
        "organizations.Organization",
        on_delete=models.CASCADE,
        related_name="crm_pipelines",
        help_text="Tenant organization this pipeline belongs to",
    )
    name = models.CharField(max_length=150)
    stages = models.JSONField(
        default=list,
        help_text="Ordered list of stage names, e.g. ['Lead', 'Qualified', 'Proposal', 'Won', 'Lost']",
    )
    is_active = models.BooleanField(
        default=True, help_text="Whether the pipeline is active"
    )

    objects = TenantManager()

    class Meta:
        db_table = "crm_pipeline"
        ordering = ["name"]
        verbose_name = "pipeline"
        verbose_name_plural = "pipelines"

    def __str__(self):
        return self.name
