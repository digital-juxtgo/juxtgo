from django.contrib.auth.mixins import AccessMixin
from django.core.exceptions import PermissionDenied, ImproperlyConfigured


class RoleRequiredMixin(AccessMixin):
    """
    CBV mixin that requires the user to have one of the specified roles.
    Superusers are automatically allowed.
    """

    required_role = None  # string or list of strings

    def dispatch(self, request, *args, **kwargs):
        if request.user.is_authenticated and request.user.is_superuser:
            return super().dispatch(request, *args, **kwargs)
        if not request.user.is_authenticated:
            return self.handle_no_permission()
        if not self.required_role:
            raise ImproperlyConfigured(
                "RoleRequiredMixin requires 'required_role' attribute."
            )
        required = (
            self.required_role
            if isinstance(self.required_role, list)
            else [self.required_role]
        )
        if not any(request.user.has_role(role) for role in required):
            raise PermissionDenied(
                f"You need one of the following roles: {', '.join(required)}"
            )
        return super().dispatch(request, *args, **kwargs)
