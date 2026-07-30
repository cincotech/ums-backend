from django.apps import AppConfig


class SearchConfig(AppConfig):
    """Configuration de l'application search."""

    default_auto_field = "django.db.models.BigAutoField"
    name = "services.search"
    verbose_name = "Typesense Search"

    def ready(self):
        """Enregistre les signaux après que les apps soient prêtes."""
        from .sync import register_signals

        register_signals()
