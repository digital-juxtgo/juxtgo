from apps.core.identity.views.auth_views import LoginView, LogoutView, RegisterView
from apps.core.identity.views.profile_views import PasswordChangeView, ProfileUpdateView

from .user_views import UserCreateView, UserListView, UserUpdateView

__all__ = [
    "LoginView",
    "LogoutView",
    "RegisterView",
    "ProfileUpdateView",
    "PasswordChangeView",
    "UserListView",
    "UserCreateView",
    "UserUpdateView",
]
