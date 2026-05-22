from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.views.generic import RedirectView

urlpatterns = [
    # Django admin fallback (not used, but good to have for debugging)
    path("admin/", admin.site.urls),

    # Core apps (identity, future API, etc.)
    path("core/", include("apps.core.urls")),

    # Dashboard (custom admin)
    path("dashboard/", include("apps.dashboard.urls")),

    # Root redirects to Dashboard
    path("", RedirectView.as_view(url="/dashboard/")),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)