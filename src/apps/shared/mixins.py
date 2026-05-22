from django.db import models


class TimestampMixin(models.Model):
    """
    Mixin that adds created_at / updated_at fields.
    Use this if you can't inherit from BaseModel (e.g., you're extending a third‑party model).
    """

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True


class AuditMixin(models.Model):
    """
    Mixin that adds created_by / updated_by fields for audit trails.
    """

    created_by = models.ForeignKey(
        "identity.User",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="+",
    )
    updated_by = models.ForeignKey(
        "identity.User",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="+",
    )

    class Meta:
        abstract = True
