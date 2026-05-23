import uuid
from django.conf import settings
from django.db import models
from apps.core.shared.models import BaseModel
from apps.core.permissions.models import Role


class Organization(BaseModel):
    name = models.CharField(max_length=150)
    slug = models.SlugField(unique=True, max_length=200)
    is_active = models.BooleanField(default=True)

    class Meta:
        db_table = "organization"
        ordering = ["name"]

    def __str__(self):
        return self.name


class OrganizationMembership(BaseModel):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="memberships",
    )
    organization = models.ForeignKey(
        Organization,
        on_delete=models.CASCADE,
        related_name="memberships",
    )
    role = models.ForeignKey(
        Role,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
    )

    class Meta:
        db_table = "organization_membership"
        unique_together = ("user", "organization")

    def __str__(self):
        return f"{self.user.email} in {self.organization.name}"


class OrganizationInvitation(BaseModel):
    organization = models.ForeignKey(
        Organization,
        on_delete=models.CASCADE,
        related_name="invitations",
    )
    email = models.EmailField()
    invited_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
    )
    token = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    accepted = models.BooleanField(default=False)

    class Meta:
        db_table = "organization_invitation"

    def __str__(self):
        return f"Invitation to {self.email} for {self.organization.name}"
