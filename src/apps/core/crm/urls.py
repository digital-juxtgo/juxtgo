from django.urls import path
from . import views

app_name = "crm"

urlpatterns = [
    # Companies
    path("companies/", views.CompanyListView.as_view(), name="company_list"),
    path("companies/create/", views.CompanyCreateView.as_view(), name="company_create"),
    path(
        "companies/<uuid:pk>/edit/",
        views.CompanyUpdateView.as_view(),
        name="company_edit",
    ),
    path(
        "companies/<uuid:pk>/delete/",
        views.CompanyDeleteView.as_view(),
        name="company_delete",
    ),
    # Contacts
    path("contacts/", views.ContactListView.as_view(), name="contact_list"),
    path("contacts/create/", views.ContactCreateView.as_view(), name="contact_create"),
    path(
        "contacts/<uuid:pk>/edit/",
        views.ContactUpdateView.as_view(),
        name="contact_edit",
    ),
    path(
        "contacts/<uuid:pk>/delete/",
        views.ContactDeleteView.as_view(),
        name="contact_delete",
    ),
    # Pipelines
    path("pipelines/", views.PipelineListView.as_view(), name="pipeline_list"),
    path(
        "pipelines/create/", views.PipelineCreateView.as_view(), name="pipeline_create"
    ),
    path(
        "pipelines/<uuid:pk>/edit/",
        views.PipelineUpdateView.as_view(),
        name="pipeline_edit",
    ),
    path(
        "pipelines/<uuid:pk>/delete/",
        views.PipelineDeleteView.as_view(),
        name="pipeline_delete",
    ),
    # Deals
    path("deals/", views.DealListView.as_view(), name="deal_list"),
    path("deals/create/", views.DealCreateView.as_view(), name="deal_create"),
    path("deals/<uuid:pk>/edit/", views.DealUpdateView.as_view(), name="deal_edit"),
    path("deals/<uuid:pk>/delete/", views.DealDeleteView.as_view(), name="deal_delete"),
]
