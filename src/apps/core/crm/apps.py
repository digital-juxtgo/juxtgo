from django.apps import AppConfig


class CrmConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "apps.core.crm"
    label = "crm"
    verbose_name = "Customer Relationship Management"
