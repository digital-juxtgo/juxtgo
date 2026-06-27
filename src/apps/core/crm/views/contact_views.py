from django.contrib import messages
from django.shortcuts import redirect, render
from django.urls import reverse_lazy
from django.views import View
from apps.core.shared.views.base import BaseListView, BaseCreateView, BaseUpdateView
from ..selectors import ContactSelector, CompanySelector
from ..services import ContactService


class ContactListView(BaseListView):
    template_name = "crm/contact/list.html"
    context_object_name = "contacts"
    page_title = "Contacts"
    add_url = reverse_lazy("core:crm:contact_create")

    def get_data(self, request):
        return ContactSelector.list_all()


class ContactCreateView(BaseCreateView):
    template_name = "crm/contact/form.html"
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
        ContactService.create(data)

    def add_extra_context(self, request, context):
        context["companies"] = CompanySelector.list_all()


class ContactUpdateView(BaseUpdateView):
    model = "crm.Contact"
    template_name = "crm/contact/form.html"
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
        ContactService.update(str(obj.pk), data)

    def add_extra_context(self, request, context):
        context["companies"] = CompanySelector.list_all()


class ContactDeleteView(View):
    template_name = "crm/confirm_delete.html"
    success_url = reverse_lazy("core:crm:contact_list")

    def get(self, request, pk):
        contact = ContactSelector.get_detail(pk)
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
            ContactService.delete(pk)
            messages.success(request, "Contact deleted.")
        except Exception as e:
            messages.error(request, str(e))
        return redirect(self.success_url)
