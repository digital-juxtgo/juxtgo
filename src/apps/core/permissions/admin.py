from django.contrib import admin
from .models import Role


@admin.register(Role)
class RoleAdmin(admin.ModelAdmin):
    list_display = ("name", "display_name", "is_system_role")
    search_fields = ("name", "display_name")
