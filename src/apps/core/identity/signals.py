from django.db.models.signals import post_save
from django.dispatch import receiver
from django.conf import settings
from .models.profile import Profile


@receiver(post_save, sender=settings.AUTH_USER_MODEL)
def create_user_profile(sender, instance, created, **kwargs):
    """Automatically create a Profile instance when a new User is created."""
    if created:
        Profile.objects.get_or_create(user=instance)


@receiver(post_save, sender=settings.AUTH_USER_MODEL)
def save_user_profile(sender, instance, **kwargs):
    """Ensure the profile is saved when the user is saved."""
    if hasattr(instance, "profile"):
        instance.profile.save()
