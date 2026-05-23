from django.urls import path, include

app_name = "core"

urlpatterns = [
    path("identity/", include("apps.core.identity.urls")),
    path("permissions/", include("apps.core.permissions.urls")),
    path("organizations/", include("apps.core.organizations.urls")),
]
