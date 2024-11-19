from django.apps import AppConfig

class AlyGtdConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "ALY_GTD"

    def ready(self):
        from .models import SequenceManager
        SequenceManager.initialize()
