"""Django app configuration for codecompare."""
from django.apps import AppConfig


class CodecompareConfig(AppConfig):
    name = "codecompare"
    verbose_name = "CodeCompare"
    default_auto_field = "django.db.models.BigAutoField"

    def ready(self) -> None:
        try:
            from codecompare.core.registry import load_default_plugins
            load_default_plugins()
        except Exception:
            pass
