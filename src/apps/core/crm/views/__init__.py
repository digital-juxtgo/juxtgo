from .company_views import (
    CompanyListView,
    CompanyCreateView,
    CompanyUpdateView,
    CompanyDeleteView,
)
from .contact_views import (
    ContactListView,
    ContactCreateView,
    ContactUpdateView,
    ContactDeleteView,
)
from .pipeline_views import (
    PipelineListView,
    PipelineCreateView,
    PipelineUpdateView,
    PipelineDeleteView,
)
from .deal_views import DealListView, DealCreateView, DealUpdateView, DealDeleteView

__all__ = [
    "CompanyListView",
    "CompanyCreateView",
    "CompanyUpdateView",
    "CompanyDeleteView",
    "ContactListView",
    "ContactCreateView",
    "ContactUpdateView",
    "ContactDeleteView",
    "PipelineListView",
    "PipelineCreateView",
    "PipelineUpdateView",
    "PipelineDeleteView",
    "DealListView",
    "DealCreateView",
    "DealUpdateView",
    "DealDeleteView",
]
