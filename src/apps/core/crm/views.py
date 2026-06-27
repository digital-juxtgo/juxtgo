from django.shortcuts import render

# Create your views here.
from django.contrib import messages
from django.shortcuts import redirect, render
from django.urls import reverse_lazy
from django.views import View
from apps.core.shared.views.base import BaseListView, BaseCreateView, BaseUpdateView
from . import selectors, services


# ---------- Company Views ----------
class CompanyListView(BaseListView):
    template_name = "crm/company_list.html"
    context_object_name = "companies"
    page_title = "Companies"
    add_url = reverse_lazy("core:crm:company_create")

    def get_data(self, request):
        return selectors.CompanySelector.list_all()


class CompanyCreateView(BaseCreateView):
    template_name = "crm/company_form.html"
    success_url = reverse_lazy("core:crm:company_list")
    page_title = "Create Company"

    def save_object(self, request):
        data = {
            "name": request.POST.get("name"),
            "website": request.POST.get("website", ""),
            "industry": request.POST.get("industry", ""),
        }
        if not data["name"]:
            raise ValueError("Company name is required.")
        services.CompanyService.create(data)


class CompanyUpdateView(BaseUpdateView):
    model = "crm.Company"
    template_name = "crm/company_form.html"
    success_url = reverse_lazy("core:crm:company_list")
    page_title = "Edit Company"
    back_url = reverse_lazy("core:crm:company_list")

    def update_object(self, request, obj):
        data = {
            "name": request.POST.get("name"),
            "website": request.POST.get("website", ""),
            "industry": request.POST.get("industry", ""),
        }
        services.CompanyService.update(str(obj.pk), data)


class CompanyDeleteView(View):
    template_name = "crm/confirm_delete.html"
    success_url = reverse_lazy("core:crm:company_list")

    def get(self, request, pk):
        company = selectors.CompanySelector.get_detail(pk)
        if not company:
            messages.error(request, "Company not found.")
            return redirect(self.success_url)
        return render(
            request,
            self.template_name,
            {"object": company, "back_url": self.success_url},
        )

    def post(self, request, pk):
        try:
            services.CompanyService.delete(pk)
            messages.success(request, "Company deleted.")
        except Exception as e:
            messages.error(request, str(e))
        return redirect(self.success_url)


# ---------- Contact Views ----------
class ContactListView(BaseListView):
    template_name = "crm/contact_list.html"
    context_object_name = "contacts"
    page_title = "Contacts"
    add_url = reverse_lazy("core:crm:contact_create")

    def get_data(self, request):
        return selectors.ContactSelector.list_all()


class ContactCreateView(BaseCreateView):
    template_name = "crm/contact_form.html"
    success_url = reverse_lazy("core:crm:contact_list")
    page_title = "Create Contact"

    def save_object(self, request):
        data = {
            "first_name": request.POST.get("first_name", ""),
            "last_name": request.POST.get("last_name", ""),
            "email": request.POST.get("email", ""),
            "phone": request.POST.get("phone", ""),
            "job_title": request.POST.get("job_title", ""),
            "company_id": request.POST.get("company_id") or None,
        }
        if not data["first_name"] or not data["last_name"]:
            raise ValueError("First and last name are required.")
        services.ContactService.create(data)


class ContactUpdateView(BaseUpdateView):
    model = "crm.Contact"
    template_name = "crm/contact_form.html"
    success_url = reverse_lazy("core:crm:contact_list")
    page_title = "Edit Contact"
    back_url = reverse_lazy("core:crm:contact_list")

    def update_object(self, request, obj):
        data = {
            "first_name": request.POST.get("first_name", ""),
            "last_name": request.POST.get("last_name", ""),
            "email": request.POST.get("email", ""),
            "phone": request.POST.get("phone", ""),
            "job_title": request.POST.get("job_title", ""),
            "company_id": request.POST.get("company_id") or None,
        }
        services.ContactService.update(str(obj.pk), data)


class ContactDeleteView(View):
    template_name = "crm/confirm_delete.html"
    success_url = reverse_lazy("core:crm:contact_list")

    def get(self, request, pk):
        contact = selectors.ContactSelector.get_detail(pk)
        if not contact:
            messages.error(request, "Contact not found.")
            return redirect(self.success_url)
        return render(
            request,
            self.template_name,
            {"object": contact, "back_url": self.success_url},
        )

    def post(self, request, pk):
        try:
            services.ContactService.delete(pk)
            messages.success(request, "Contact deleted.")
        except Exception as e:
            messages.error(request, str(e))
        return redirect(self.success_url)


# ---------- Pipeline Views ----------
class PipelineListView(BaseListView):
    template_name = "crm/pipeline_list.html"
    context_object_name = "pipelines"
    page_title = "Sales Pipelines"
    add_url = reverse_lazy("core:crm:pipeline_create")

    def get_data(self, request):
        return selectors.PipelineSelector.list_all()


class PipelineCreateView(BaseCreateView):
    template_name = "crm/pipeline_form.html"
    success_url = reverse_lazy("core:crm:pipeline_list")
    page_title = "Create Pipeline"

    def save_object(self, request):
        name = request.POST.get("name", "")
        stages_str = request.POST.get("stages", "")
        stages = [s.strip() for s in stages_str.split(",") if s.strip()]
        if not name:
            raise ValueError("Pipeline name is required.")
        services.PipelineService.create({"name": name, "stages": stages})


class PipelineUpdateView(BaseUpdateView):
    model = "crm.Pipeline"
    template_name = "crm/pipeline_form.html"
    success_url = reverse_lazy("core:crm:pipeline_list")
    page_title = "Edit Pipeline"
    back_url = reverse_lazy("core:crm:pipeline_list")

    def update_object(self, request, obj):
        data = {
            "name": request.POST.get("name", ""),
            "stages": [
                s.strip()
                for s in request.POST.get("stages", "").split(",")
                if s.strip()
            ],
        }
        services.PipelineService.update(str(obj.pk), data)


class PipelineDeleteView(View):
    template_name = "crm/confirm_delete.html"
    success_url = reverse_lazy("core:crm:pipeline_list")

    def get(self, request, pk):
        pipeline = selectors.PipelineSelector.get_detail(pk)
        if not pipeline:
            messages.error(request, "Pipeline not found.")
            return redirect(self.success_url)
        return render(
            request,
            self.template_name,
            {"object": pipeline, "back_url": self.success_url},
        )

    def post(self, request, pk):
        try:
            services.PipelineService.delete(pk)
            messages.success(request, "Pipeline deleted.")
        except Exception as e:
            messages.error(request, str(e))
        return redirect(self.success_url)


# ---------- Deal Views ----------
class DealListView(BaseListView):
    template_name = "crm/deal_list.html"
    context_object_name = "deals"
    page_title = "Deals"
    add_url = reverse_lazy("core:crm:deal_create")

    def get_data(self, request):
        return selectors.DealSelector.list_all()

    def add_extra_context(self, request, context):
        context["pipelines"] = selectors.PipelineSelector.list_all()
        context["contacts"] = selectors.ContactSelector.list_all()
        context["companies"] = selectors.CompanySelector.list_all()


class DealCreateView(BaseCreateView):
    template_name = "crm/deal_form.html"
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
        services.DealService.create(data)


class DealUpdateView(BaseUpdateView):
    model = "crm.Deal"
    template_name = "crm/deal_form.html"
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
        services.DealService.update(str(obj.pk), data)


class DealDeleteView(View):
    template_name = "crm/confirm_delete.html"
    success_url = reverse_lazy("core:crm:deal_list")

    def get(self, request, pk):
        deal = selectors.DealSelector.get_detail(pk)
        if not deal:
            messages.error(request, "Deal not found.")
            return redirect(self.success_url)
        return render(
            request, self.template_name, {"object": deal, "back_url": self.success_url}
        )

    def post(self, request, pk):
        try:
            services.DealService.delete(pk)
            messages.success(request, "Deal deleted.")
        except Exception as e:
            messages.error(request, str(e))
        return redirect(self.success_url)
