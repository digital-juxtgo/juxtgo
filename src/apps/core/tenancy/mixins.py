class TenantQuerysetMixin:
    """
    Mixin for Django models that automatically assigns the current organization
    when creating a new record.
    """

    def save(self, *args, **kwargs):
        from apps.core.tenancy.middleware import get_current_org_id

        org_id = get_current_org_id()
        if org_id and hasattr(self, "organization_id"):
            self.organization_id = org_id
        super().save(*args, **kwargs)
