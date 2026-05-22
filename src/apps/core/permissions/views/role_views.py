from django.contrib import messages
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse_lazy
from django.views import View
from apps.shared.views.base import BaseListView, BaseCreateView, BaseUpdateView
from apps.core.identity.selectors import UserSelector
from apps.core.identity.services import UserService
from ..services.role_service import RoleService
from ..selectors.role_selector import RoleSelector
from ..forms import RoleForm
from ..models import Role
from ..mixins import RoleRequiredMixin


class RoleAccessListView(RoleRequiredMixin, BaseListView):
    required_role = "admin"
    template_name = "permissions/roles/role_access.html"
    context_object_name = "roles"
    page_title = "Role & Access"

    def get_data(self, request):
        return RoleSelector.list_roles()

    def add_extra_context(self, request, context):
        context["modal_id"] = "addRoleModal"


class RoleCreateView(RoleRequiredMixin, BaseCreateView):
    required_role = "admin"
    template_name = "permissions/roles/form.html"
    success_url = reverse_lazy("core:permissions:role_list")
    success_message = "Role created successfully."

    def save_object(self, request):
        name = request.POST.get("name")
        display_name = request.POST.get("display_name")
        description = request.POST.get("description", "")
        if not name or not display_name:
            raise ValueError("Name and display name are required.")
        RoleService.create_role(name, display_name, description)


class RoleUpdateView(RoleRequiredMixin, BaseUpdateView):
    required_role = "admin"
    model = "permissions.Role"
    template_name = "permissions/roles/form.html"
    success_url = reverse_lazy("core:permissions:role_list")
    success_message = "Role updated successfully."
    back_url = reverse_lazy("core:permissions:role_list")

    def update_object(self, request, obj):
        data = {
            "name": request.POST.get("name"),
            "display_name": request.POST.get("display_name"),
            "description": request.POST.get("description"),
        }
        permissions = request.POST.getlist("permissions")
        if permissions:
            data["permissions"] = [int(p) for p in permissions]
        RoleService.update_role(obj.pk, data)

    def add_extra_context(self, request, context):
        role = get_object_or_404(Role, pk=context["object"].pk)
        context["form"] = RoleForm(instance=role)


class RoleDeleteView(RoleRequiredMixin, View):
    required_role = "admin"
    template_name = "permissions/roles/confirm_delete.html"
    success_url = reverse_lazy("core:permissions:role_list")

    def get(self, request, pk):
        role_dict = RoleSelector.get_role_detail(pk)
        if not role_dict:
            messages.error(request, "Role not found.")
            return redirect(self.success_url)
        return render(request, self.template_name, {"object": role_dict})

    def post(self, request, pk):
        try:
            RoleService.delete_role(pk)
            messages.success(request, "Role deleted.")
        except Exception as e:
            messages.error(request, str(e))
        return redirect(self.success_url)


class AssignRoleView(RoleRequiredMixin, View):
    required_role = "admin"
    template_name = "permissions/roles/assign_role.html"
    page_title = "Assign Role"

    def get(self, request):
        users = UserSelector.list_users()
        roles = RoleSelector.list_roles()
        return render(
            request,
            self.template_name,
            {"users": users, "roles": roles, "page_title": self.page_title},
        )

    def post(self, request):
        user_id = request.POST.get("user_id")
        role_name = request.POST.get("role_name")
        try:
            UserService.assign_role(user_id, role_name)
            messages.success(request, f"Role '{role_name}' assigned.")
        except ValueError as e:
            messages.error(request, str(e))
        return redirect("core:permissions:assign_role")


class UserRolePermissionListView(RoleRequiredMixin, BaseListView):
    required_role = "admin"
    template_name = "identity/users/user_role_permission.html"
    context_object_name = "users"
    page_title = "User Role & Permission"

    def get_data(self, request):
        return UserSelector.list_users()

    def add_extra_context(self, request, context):
        context["roles"] = RoleSelector.list_roles()

    def post(self, request):
        user_id = request.POST.get("user_id")
        action = request.POST.get("action")
        if action == "toggle_active":
            UserService.toggle_active(user_id)
            messages.success(request, "Status toggled.")
        return redirect("core:permissions:user_role_permission")
