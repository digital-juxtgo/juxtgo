from django.conf import settings
from django.db import models
from django.utils.translation import gettext_lazy as _

from apps.shared.models import BaseModel


class Profile(BaseModel):
    """
    Extensible user profile model. One-to-one with User.
    Inherits UUID, created_at, updated_at from BaseModel.
    """

    user = models.OneToOneField(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="profile"
    )
    first_name = models.CharField(_("first name"), max_length=150, blank=True)
    last_name = models.CharField(_("last name"), max_length=150, blank=True)
    avatar = models.ImageField(upload_to="avatars/", blank=True, null=True)
    bio = models.TextField(blank=True)
    metadata = models.JSONField(default=dict, blank=True)

    class Meta:
        db_table = "identity_profile"
        verbose_name = _("profile")
        verbose_name_plural = _("profiles")

    def __str__(self):
        return f"Profile for {self.user.email}"

    def get_full_name(self) -> str:
        if self.first_name and self.last_name:
            return f"{self.first_name} {self.last_name}"
        return self.user.email

    def get_initials(self) -> str:
        initials = ""
        if self.first_name:
            initials += self.first_name[0].upper()
        if self.last_name:
            initials += self.last_name[0].upper()
        return initials or self.user.email[0].upper()
