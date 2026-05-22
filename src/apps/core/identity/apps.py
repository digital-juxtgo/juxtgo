from django.apps import AppConfig

class IdentityConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "apps.core.identity"
    label = "identity"

    def ready(self):
        import apps.core.identity.signals  # noqa