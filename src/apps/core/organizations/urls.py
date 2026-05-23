from django.urls import path
from .views import (
    OrganizationListView,
    OrganizationCreateView,
    OrganizationUpdateView,
    OrganizationDeleteView,
    SwitchOrganizationView,
)

app_name = "organizations"

urlpatterns = [
    path("", OrganizationListView.as_view(), name="list"),
    path("create/", OrganizationCreateView.as_view(), name="create"),
    path("<uuid:pk>/edit/", OrganizationUpdateView.as_view(), name="edit"),
    path("<uuid:pk>/delete/", OrganizationDeleteView.as_view(), name="delete"),
    path("switch/", SwitchOrganizationView.as_view(), name="switch"),
]
