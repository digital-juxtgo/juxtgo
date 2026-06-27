from django.contrib import messages
from django.shortcuts import redirect, render
from django.urls import reverse_lazy
from django.views import View
from apps.core.shared.views.base import BaseListView, BaseCreateView, BaseUpdateView
from ..selectors import CompanySelector
from ..services import CompanyService


class CompanyListView(BaseListView):
    template_name = "crm/company/list.html"
    context_object_name = "companies"
    page_title = "Companies"
    add_url = reverse_lazy("core:crm:company_create")

    def get_data(self, request):
        return CompanySelector.list_all()


class CompanyCreateView(BaseCreateView):
    template_name = "crm/company/form.html"
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
        CompanyService.create(data)


class CompanyUpdateView(BaseUpdateView):
    model = "crm.Company"
    template_name = "crm/company/form.html"
    success_url = reverse_lazy("core:crm:company_list")
    page_title = "Edit Company"
    back_url = reverse_lazy("core:crm:company_list")

    def update_object(self, request, obj):
        data = {
            "name": request.POST.get("name"),
            "website": request.POST.get("website", ""),
            "industry": request.POST.get("industry", ""),
        }
        CompanyService.update(str(obj.pk), data)


class CompanyDeleteView(View):
    template_name = "crm/confirm_delete.html"
    success_url = reverse_lazy("core:crm:company_list")

    def get(self, request, pk):
        company = CompanySelector.get_detail(pk)
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
            CompanyService.delete(pk)
            messages.success(request, "Company deleted.")
        except Exception as e:
            messages.error(request, str(e))
        return redirect(self.success_url)
