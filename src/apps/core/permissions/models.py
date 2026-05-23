from django.contrib.auth.models import Group
from django.db import models
from apps.core.shared.models import BaseModel


class Role(BaseModel):
    """
    Custom role model wrapping Django's Group.
    Inherits UUID pk, created_at, updated_at from BaseModel.
    """

    name = models.CharField(max_length=50, unique=True)
    display_name = models.CharField(max_length=100)
    group = models.OneToOneField(
        Group,
        on_delete=models.CASCADE,
        related_name="identity_role",
        null=True,
        blank=True,
    )
    description = models.TextField(blank=True)
    is_system_role = models.BooleanField(default=False)

    class Meta:
        db_table = "permissions_role"
        verbose_name = "role"
        verbose_name_plural = "roles"
        ordering = ["name"]

    def __str__(self):
        return self.display_name

    def save(self, *args, **kwargs):
        if not self.group_id:
            group, _ = Group.objects.get_or_create(name=self.name)
            self.group = group
        super().save(*args, **kwargs)
