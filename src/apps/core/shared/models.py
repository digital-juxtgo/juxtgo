import uuid
from django.conf import settings
from django.db import models


class BaseModel(models.Model):
    """
    Abstract base model that provides a UUID primary key and auto‑timestamps.
    Every model in JuxtGo OS should inherit from this.
    """

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="%(app_label)s_%(class)s_created_by",
    )
    updated_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="%(app_label)s_%(class)s_updated_by",
    )

    class Meta:
        abstract = True


class SoftDeleteModel(models.Model):
    """
    Abstract model that adds a soft‑delete flag.
    """

    is_deleted = models.BooleanField(default=False)

    class Meta:
        abstract = True

    def soft_delete(self, *args, **kwargs):
        self.is_deleted = True
        self.save(update_fields=["is_deleted"])
