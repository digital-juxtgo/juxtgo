from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth import update_session_auth_hash
from django.contrib.auth.forms import PasswordChangeForm
from django.contrib import messages
from django.shortcuts import render, redirect
from django.urls import reverse_lazy
from django.views import View
from ..services import UserService


class ProfileUpdateView(LoginRequiredMixin, View):
    template_name = "identity/users/profile.html"
    success_url = reverse_lazy("core:identity:profile")

    def get(self, request):
        profile = request.user.profile
        context = {"profile": profile}
        return render(request, self.template_name, context)

    def post(self, request):
        data = {
            "first_name": request.POST.get("first_name", "").strip(),
            "last_name": request.POST.get("last_name", "").strip(),
            "bio": request.POST.get("bio", "").strip(),
        }
        avatar = request.FILES.get("avatar")
        if avatar:
            data["avatar"] = avatar
        try:
            UserService.update_profile(str(request.user.id), data)
            messages.success(request, "Profile updated successfully.")
        except Exception as e:
            messages.error(request, f"Update failed: {e}")
        return redirect(self.success_url)


class PasswordChangeView(LoginRequiredMixin, View):
    success_url = reverse_lazy("core:identity:profile")

    def post(self, request):
        form = PasswordChangeForm(user=request.user, data=request.POST)
        if form.is_valid():
            form.save()
            update_session_auth_hash(request, form.user)
            messages.success(request, "Password changed.")
        else:
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f"{field}: {error}")
        return redirect(self.success_url)
