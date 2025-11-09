from django.apps import AppConfig


class ParentAppConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "services.core_service.student_module.parent_app"
