from django.urls import path
from .views.role_views import (
    AssignRoleView,
    RoleAccessListView,
    RoleCreateView,
    RoleDeleteView,
    RoleUpdateView,
    UserRolePermissionListView,
)

app_name = "permissions"

urlpatterns = [
    path(
        "users/roles-permissions/",
        UserRolePermissionListView.as_view(),
        name="user_role_permission",
    ),
    path("roles/", RoleAccessListView.as_view(), name="role_list"),
    path("roles/create/", RoleCreateView.as_view(), name="role_create"),
    path("roles/<uuid:pk>/edit/", RoleUpdateView.as_view(), name="role_edit"),
    path("roles/<uuid:pk>/delete/", RoleDeleteView.as_view(), name="role_delete"),
    path("roles/assign/", AssignRoleView.as_view(), name="assign_role"),
]
