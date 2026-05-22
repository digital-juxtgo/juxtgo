from django.contrib.auth import login as auth_login, logout as auth_logout
from django.contrib import messages
from django.shortcuts import render, redirect
from django.views import View
from apps.core.identity.selectors import UserSelector
from apps.core.identity.services import UserService


class LoginView(View):
    """Handles user login."""

    template_name = "identity/login.html"

    def get(self, request):
        if request.user.is_authenticated:
            return redirect("dashboard:index")
        return render(request, self.template_name)

    def post(self, request):
        email = request.POST.get("email", "").strip().lower()
        password = request.POST.get("password")
        user_dict = UserSelector.get_user_by_email(email)
        if user_dict is None:
            messages.error(request, "Invalid email or password.")
            return render(request, self.template_name)
        # need actual user object for login
        from django.contrib.auth import authenticate

        user = authenticate(request, username=email, password=password)
        if user and user.is_active:
            auth_login(request, user)
            messages.success(request, f"Welcome, {user.email}!")
            return redirect("dashboard:index")
        messages.error(request, "Invalid email or password.")
        return render(request, self.template_name)


class LogoutView(View):
    """Handles user logout."""

    def get(self, request):
        auth_logout(request)
        messages.info(request, "You have been logged out.")
        return redirect("core:identity:login")


class RegisterView(View):
    """Handles new user registration."""

    template_name = "identity/register.html"

    def get(self, request):
        if request.user.is_authenticated:
            return redirect("dashboard:index")
        return render(request, self.template_name)

    def post(self, request):
        email = request.POST.get("email", "").strip().lower()
        password = request.POST.get("password")
        first_name = request.POST.get("first_name", "").strip()
        last_name = request.POST.get("last_name", "").strip()

        errors = {}
        if not email or "@" not in email:
            errors["email"] = "Valid email required."
        if not password or len(password) < 8:
            errors["password"] = "Password must be at least 8 characters."
        if UserSelector.user_exists(email):
            errors["email"] = "Email already registered."

        if errors:
            return render(
                request, self.template_name, {"errors": errors, "form": request.POST}
            )

        try:
            user = UserService.register_user(email, password, first_name, last_name)
            auth_login(request, user)
            messages.success(request, "Registration successful! Welcome aboard.")
            return redirect("dashboard:index")
        except Exception as e:
            messages.error(request, f"Registration failed: {e}")
            return render(request, self.template_name, {"form": request.POST})
