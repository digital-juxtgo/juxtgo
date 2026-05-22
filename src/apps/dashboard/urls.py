from django.urls import path
from .views.index import HomeView

app_name = "dashboard"

urlpatterns = [
    path("", HomeView.as_view(), name="index"),
]