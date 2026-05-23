import logging
from django.contrib import messages
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError
from django.shortcuts import render, redirect
from django.urls import reverse_lazy
from django.views import View
from apps.core.shared.views.base import BaseListView, BaseCreateView, BaseUpdateView
from apps.core.identity.selectors.user_selector import UserSelector
from apps.core.identity.services.user_service import UserService
from apps.core.permissions.mixins import RoleRequiredMixin

logger = logging.getLogger(__name__)


class UserListView(RoleRequiredMixin, BaseListView):
    required_role = ["admin", "manager"]
    template_name = "identity/users/list.html"
    context_object_name = "users"
    page_title = "User Management"
    add_url = reverse_lazy("core:identity:user_create")

    def get_data(self, request):
        search = request.GET.get("search", "")
        status = request.GET.get("status", "")
        return UserSelector.list_users(search=search, status=status)


class UserCreateView(RoleRequiredMixin, BaseCreateView):
    required_role = "admin"
    template_name = "identity/users/form.html"
    success_url = reverse_lazy("core:identity:user_list")
    success_message = "User created successfully."
    back_url = reverse_lazy("core:identity:user_list")

    def save_object(self, request):
        email = request.POST.get("email", "").strip().lower()
        password = request.POST.get("password", "")
        first_name = request.POST.get("first_name", "").strip()
        last_name = request.POST.get("last_name", "").strip()
        bio = request.POST.get("bio", "").strip()
        avatar = request.FILES.get("avatar")

        errors = {}
        if not email or "@" not in email:
            errors["email"] = "A valid email is required."
        elif UserSelector.user_exists(email):
            errors["email"] = "A user with this email already exists."

        if not password:
            errors["password"] = "Password is required."
        else:
            try:
                validate_password(password)
            except ValidationError as e:
                errors["password"] = " ".join(e.messages)

        if errors:
            raise ValidationError(errors)

        UserService.register_user(
            email=email,
            password=password,
            first_name=first_name,
            last_name=last_name,
            bio=bio,
            avatar=avatar,
        )


class UserUpdateView(RoleRequiredMixin, BaseUpdateView):
    required_role = "admin"
    model = "identity.User"  # string reference
    template_name = "identity/users/form.html"
    success_url = reverse_lazy("core:identity:user_list")
    success_message = "User updated successfully."
    back_url = reverse_lazy("core:identity:user_list")

    def update_object(self, request, obj):
        data = {
            "first_name": request.POST.get("first_name", "").strip(),
            "last_name": request.POST.get("last_name", "").strip(),
            "bio": request.POST.get("bio", "").strip(),
        }
        avatar = request.FILES.get("avatar")
        if avatar:
            data["avatar"] = avatar
        UserService.update_profile(str(obj.pk), data)


class UserDeleteView(RoleRequiredMixin, View):
    required_role = "admin"
    template_name = "identity/users/confirm_delete.html"
    success_url = reverse_lazy("core:identity:user_list")

    def get(self, request, pk):
        user_dict = UserSelector.get_user_detail(pk)
        if not user_dict:
            messages.error(request, "User not found.")
            return redirect(self.success_url)
        return render(request, self.template_name, {"object": user_dict})

    def post(self, request, pk):
        try:
            UserService.delete_user(pk)
            messages.success(request, "User deleted.")
        except Exception as e:
            messages.error(request, str(e))
        return redirect(self.success_url)
