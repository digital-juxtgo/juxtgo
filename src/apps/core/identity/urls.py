from django.urls import path
from apps.core.identity.views.auth_views import LoginView, LogoutView, RegisterView
from apps.core.identity.views.profile_views import PasswordChangeView, ProfileUpdateView

from apps.core.identity.views.user_views import (
    UserCreateView,
    UserListView,
    UserUpdateView,
    UserDeleteView,
)

app_name = "identity"

urlpatterns = [
    # Authentication
    path("login/", LoginView.as_view(), name="login"),
    path("logout/", LogoutView.as_view(), name="logout"),
    path("register/", RegisterView.as_view(), name="register"),
    # Self-service
    path("profile/", ProfileUpdateView.as_view(), name="profile"),
    path("password-change/", PasswordChangeView.as_view(), name="password_change"),
    # User management (admin area)
    path("users/", UserListView.as_view(), name="user_list"),
    path("users/create/", UserCreateView.as_view(), name="user_create"),
    path("users/<uuid:pk>/edit/", UserUpdateView.as_view(), name="user_edit"),
    path("users/<uuid:pk>/delete/", UserDeleteView.as_view(), name="user_delete"),
]
