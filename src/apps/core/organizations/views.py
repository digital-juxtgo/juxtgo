from django.contrib import messages
from django.shortcuts import redirect, render
from django.urls import reverse_lazy
from django.views import View
from apps.core.shared.views.base import BaseListView, BaseCreateView, BaseUpdateView
from apps.core.permissions.mixins import RoleRequiredMixin
from .selectors import OrganizationSelector
from .services import OrganizationService


class OrganizationListView(BaseListView):
    template_name = "organizations/list.html"
    context_object_name = "organizations"
    page_title = "Organizations"
    add_url = reverse_lazy("core:organizations:create")

    def get_data(self, request):
        return OrganizationSelector.list_for_user(request.user)


class OrganizationCreateView(BaseCreateView):
    template_name = "organizations/form.html"
    success_url = reverse_lazy("core:organizations:list")
    page_title = "Create Organization"
    back_url = reverse_lazy("core:organizations:list")

    def save_object(self, request):
        name = request.POST.get("name")
        if not name:
            raise ValueError("Organisation name is required.")
        OrganizationService.create_organization(name, request.user)


class OrganizationUpdateView(BaseUpdateView):
    model = "organizations.Organization"
    template_name = "organizations/form.html"
    success_url = reverse_lazy("core:organizations:list")
    page_title = "Edit Organization"
    back_url = reverse_lazy("core:organizations:list")

    def update_object(self, request, obj):
        name = request.POST.get("name")
        if not name:
            raise ValueError("Organisation name is required.")
        OrganizationService.update_organization(obj.pk, name)


class OrganizationDeleteView(RoleRequiredMixin, View):
    required_role = "admin"  # only admins can delete orgs
    template_name = "organizations/confirm_delete.html"
    success_url = reverse_lazy("core:organizations:list")

    def get(self, request, pk):
        org_dict = OrganizationSelector.get_detail(pk)
        if not org_dict:
            messages.error(request, "Organization not found.")
            return redirect(self.success_url)
        return render(request, self.template_name, {"object": org_dict})

    def post(self, request, pk):
        try:
            OrganizationService.delete_organization(pk)
            messages.success(request, "Organization deleted.")
        except Exception as e:
            messages.error(request, str(e))
        return redirect(self.success_url)


class SwitchOrganizationView(View):
    def post(self, request):
        org_id = request.POST.get("organization_id")
        if org_id:
            try:
                org = OrganizationService.switch_organization(request.user, org_id)
                request.session["current_org_id"] = str(org.id)
                request.session["current_org_name"] = org.name
                messages.success(request, f"Switched to {org.name}.")
            except ValueError as e:
                messages.error(request, str(e))
        return redirect("dashboard:index")
