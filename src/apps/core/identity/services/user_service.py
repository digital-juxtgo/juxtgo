import logging, uuid, os
from django.db import transaction
from django.contrib.auth import get_user_model
from apps.core.permissions.models import Role
from apps.core.identity.selectors import UserSelector

User = get_user_model()
logger = logging.getLogger(__name__)


class UserService:
    @classmethod
    def register_user(
        cls, email, password, first_name="", last_name="", bio="", avatar=None, **extra
    ):
        email = email.lower().strip()
        if UserSelector.user_exists(email):
            raise ValueError("A user with this email already exists.")
        with transaction.atomic():
            user = User.objects.create_user(email=email, password=password, **extra)
            profile = user.profile  # type: ignore[attr-defined]
            profile.first_name = first_name
            profile.last_name = last_name
            profile.bio = bio
            if avatar:
                ext = avatar.name.split(".")[-1] if "." in avatar.name else "jpg"
                base = (
                    f"{first_name}_{last_name}".strip().lower().replace(" ", "_")
                    or "user"
                )
                unique_id = uuid.uuid4().hex[:8]
                filename = f"{base}_{unique_id}.{ext}"
                avatar.name = filename
                profile.avatar = avatar
            profile.save()
            logger.info("User registered: %s (ID: %s)", user.email, user.pk)
        return user  # return ORM object for potential further processing (but not passed to templates)

    @classmethod
    def update_profile(cls, user_id: str, profile_data: dict):
        user = User.objects.get(id=user_id)
        profile = user.profile  # type: ignore[attr-defined]
        allowed = {"first_name", "last_name", "avatar", "bio", "metadata"}
        for field, value in profile_data.items():
            if field in allowed:
                if field == "avatar" and value:
                    if profile.avatar and os.path.isfile(profile.avatar.path):
                        os.remove(profile.avatar.path)
                    ext = value.name.split(".")[-1] if "." in value.name else "jpg"
                    base = (
                        profile.first_name.strip().lower().replace(" ", "_") or "user"
                    )
                    new_filename = f"{base}_{user.id}.{ext}"  # type: ignore[attr-defined]
                    value.name = new_filename
                setattr(profile, field, value)
            else:
                logger.warning(
                    "Ignored disallowed field '%s' for user %s", field, user.email
                )
        profile.save()
        logger.info("User profile updated: %s", user.email)

    @classmethod
    def toggle_active(cls, user_id: str) -> bool:
        user = User.objects.get(id=user_id)
        user.is_active = not user.is_active
        user.save(update_fields=["is_active"])
        return user.is_active

    @classmethod
    def assign_role(cls, user_id: str, role_name: str):
        user = User.objects.get(id=user_id)
        try:
            role = Role.objects.get(name__iexact=role_name)
        except Role.DoesNotExist:
            raise ValueError(f"Role '{role_name}' does not exist.")
        user.groups.clear()
        user.groups.add(role.group)
        logger.info("Role '%s' assigned to user %s", role_name, user.email)

    @classmethod
    def delete_user(cls, user_id: str):
        user = User.objects.get(id=user_id)
        try:
            profile = user.profile  # type: ignore[attr-defined]
            if profile.avatar and os.path.isfile(profile.avatar.path):
                os.remove(profile.avatar.path)
        except Exception as e:
            logger.warning("Could not delete avatar for user %s: %s", user.email, e)
        user.delete()
        logger.info("User deleted: %s", user.email)
