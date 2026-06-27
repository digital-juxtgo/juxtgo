from django.contrib import messages
from django.shortcuts import redirect, render
from django.urls import reverse_lazy
from django.views import View
from apps.core.shared.views.base import BaseListView, BaseCreateView, BaseUpdateView
from ..selectors import DealSelector, PipelineSelector, ContactSelector, CompanySelector
from ..services import DealService


class DealListView(BaseListView):
    template_name = "crm/deal/list.html"
    context_object_name = "deals"
    page_title = "Deals"
    add_url = reverse_lazy("core:crm:deal_create")

    def get_data(self, request):
        return DealSelector.list_all()

    def add_extra_context(self, request, context):
        context["pipelines"] = PipelineSelector.list_all()
        context["contacts"] = ContactSelector.list_all()
        context["companies"] = CompanySelector.list_all()


class DealCreateView(BaseCreateView):
    template_name = "crm/deal/form.html"
    success_url = reverse_lazy("core:crm:deal_list")
    page_title = "Create Deal"

    def save_object(self, request):
        data = {
            "title": request.POST.get("title"),
            "pipeline_id": request.POST.get("pipeline_id"),
            "stage": request.POST.get("stage"),
            "contact_id": request.POST.get("contact_id") or None,
            "company_id": request.POST.get("company_id") or None,
            "amount": request.POST.get("amount") or None,
            "expected_close_date": request.POST.get("expected_close_date") or None,
        }
        if not data["title"] or not data["pipeline_id"] or not data["stage"]:
            raise ValueError("Title, pipeline, and stage are required.")
        DealService.create(data)

    def add_extra_context(self, request, context):
        context["pipelines"] = PipelineSelector.list_all()
        context["contacts"] = ContactSelector.list_all()
        context["companies"] = CompanySelector.list_all()
        pipeline_id = request.POST.get("pipeline_id")
        if pipeline_id:
            pipeline = PipelineSelector.get_detail(pipeline_id)
            context["stages"] = pipeline.get("stages", []) if pipeline else []
        else:
            context["stages"] = []


class DealUpdateView(BaseUpdateView):
    model = "crm.Deal"
    template_name = "crm/deal/form.html"
    success_url = reverse_lazy("core:crm:deal_list")
    page_title = "Edit Deal"
    back_url = reverse_lazy("core:crm:deal_list")

    def update_object(self, request, obj):
        data = {
            "title": request.POST.get("title"),
            "pipeline_id": request.POST.get("pipeline_id"),
            "stage": request.POST.get("stage"),
            "contact_id": request.POST.get("contact_id") or None,
            "company_id": request.POST.get("company_id") or None,
            "amount": request.POST.get("amount") or None,
            "expected_close_date": request.POST.get("expected_close_date") or None,
        }
        DealService.update(str(obj.pk), data)

    def add_extra_context(self, request, context):
        context["pipelines"] = PipelineSelector.list_all()
        context["contacts"] = ContactSelector.list_all()
        context["companies"] = CompanySelector.list_all()
        deal = DealSelector.get_detail(str(context["object"].pk))
        if deal and deal.get("pipeline_id"):
            pipeline = PipelineSelector.get_detail(deal["pipeline_id"])
            context["stages"] = pipeline.get("stages", []) if pipeline else []
        else:
            context["stages"] = []


class DealDeleteView(View):
    template_name = "crm/confirm_delete.html"
    success_url = reverse_lazy("core:crm:deal_list")

    def get(self, request, pk):
        deal = DealSelector.get_detail(pk)
        if not deal:
            messages.error(request, "Deal not found.")
            return redirect(self.success_url)
        return render(
            request, self.template_name, {"object": deal, "back_url": self.success_url}
        )

    def post(self, request, pk):
        try:
            DealService.delete(pk)
            messages.success(request, "Deal deleted.")
        except Exception as e:
            messages.error(request, str(e))
        return redirect(self.success_url)
