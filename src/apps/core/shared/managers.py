from django.db import models
from apps.core.tenancy.middleware import get_current_org_id


class TenantManager(models.Manager):
    """
    Automatically filters querysets by the current organization.
    Use this manager for any model that should be tenant‑scoped.
    Example:
        class Contact(BaseModel):
            organization = models.ForeignKey(...)
            objects = TenantManager()
    """

    def get_queryset(self):
        qs = super().get_queryset()
        org_id = get_current_org_id()
        if org_id:
            return qs.filter(organization_id=org_id)
        return qs
