from django.views.generic import TemplateView
from django.contrib.auth.mixins import LoginRequiredMixin
from apps.core.permissions.selectors import RoleSelector
from apps.core.identity.selectors import UserSelector


class HomeView(LoginRequiredMixin, TemplateView):
    template_name = "dashboard/index.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        total_users = UserSelector.count_all()
        active_users = UserSelector.count_active()
        new_today = UserSelector.count_joined_today()
        total_roles = len(RoleSelector.list_roles())

        if total_users > 0:
            active_percentage = round((active_users / total_users) * 100)
        else:
            active_percentage = 0

        latest_users = UserSelector.list_latest(6)

        context.update(
            {
                "total_users": total_users,
                "active_users": active_users,
                "active_percentage": active_percentage,
                "new_today": new_today,
                "total_roles": total_roles,
                "latest_users": latest_users,
            }
        )
        return context
