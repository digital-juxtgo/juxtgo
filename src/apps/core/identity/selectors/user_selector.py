from typing import List, Dict, Optional
from django.contrib.auth import get_user_model
from django.db import models as db_models

User = get_user_model()


class UserSelector:
    @staticmethod
    def user_exists(email: str) -> bool:
        return User.objects.filter(email__iexact=email).exists()

    @staticmethod
    def get_user_by_email(email: str) -> Optional[Dict]:
        try:
            user = User.objects.select_related("profile").get(email__iexact=email)
            return UserSelector._user_to_dict(user)
        except User.DoesNotExist:
            return None

    @staticmethod
    def list_users(search="", status="", ordering="-date_joined") -> List[Dict]:
        qs = User.objects.select_related("profile").all()
        if search:
            qs = qs.filter(
                db_models.Q(email__icontains=search)
                | db_models.Q(profile__first_name__icontains=search)
                | db_models.Q(profile__last_name__icontains=search)
            )
        if status == "active":
            qs = qs.filter(is_active=True)
        elif status == "inactive":
            qs = qs.filter(is_active=False)
        qs = qs.order_by(ordering)
        return [UserSelector._user_to_dict(u) for u in qs]

    @staticmethod
    def get_user_detail(user_id: str) -> Optional[Dict]:
        try:
            user = User.objects.select_related("profile").get(pk=user_id)
            return UserSelector._user_to_dict(user)
        except User.DoesNotExist:
            return None

    @staticmethod
    def _user_to_dict(user) -> Dict:
        profile = user.profile
        return {
            "id": str(user.id),
            "email": user.email,
            "is_active": user.is_active,
            "is_staff": user.is_staff,
            "is_superuser": user.is_superuser,
            "is_verified": user.is_verified,
            "date_joined": user.date_joined.strftime("%Y-%m-%d %H:%M:%S"),
            "first_name": profile.first_name,
            "last_name": profile.last_name,
            "full_name": profile.get_full_name(),
            "bio": profile.bio,
            "avatar_url": profile.avatar.url if profile.avatar else None,
            "role": (
                user.groups.first().identity_role.display_name
                if user.groups.exists()
                and hasattr(user.groups.first(), "identity_role")
                else None
            ),
        }

    @staticmethod
    def count_all() -> int:
        """Return total number of users."""
        from django.contrib.auth import get_user_model

        User = get_user_model()
        return User.objects.count()

    @staticmethod
    def count_active() -> int:
        """Return number of active users."""
        from django.contrib.auth import get_user_model

        User = get_user_model()
        return User.objects.filter(is_active=True).count()

    @staticmethod
    def count_joined_today() -> int:
        """Return number of users who joined today."""
        from django.contrib.auth import get_user_model
        from datetime import date

        User = get_user_model()
        return User.objects.filter(date_joined__date=date.today()).count()

    @staticmethod
    def list_latest(limit=6) -> List[Dict]:
        """Return the most recent users as dicts."""
        from django.contrib.auth import get_user_model

        User = get_user_model()
        qs = User.objects.select_related("profile").order_by("-date_joined")[:limit]
        return [UserSelector._user_to_dict(u) for u in qs]
