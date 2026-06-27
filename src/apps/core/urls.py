from django.urls import path, include
from apps.core.shared.views.health import health_check

app_name = "core"

urlpatterns = [
    path("identity/", include("apps.core.identity.urls")),
    path("permissions/", include("apps.core.permissions.urls")),
    path("organizations/", include("apps.core.organizations.urls")),
    # health check endpoint
    path("health/", health_check, name="health"),
]
