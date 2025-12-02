from django.urls import include, path

urlpatterns = [
    path(
        "",
        include(
            "services.dependent_service.notification_module.event_notification_app.urls"
        ),
    ),
]
