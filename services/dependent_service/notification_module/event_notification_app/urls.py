from rest_framework.routers import DefaultRouter

from services.dependent_service.notification_module.event_notification_app.views import (
    NotificationViewSet,
)

router = DefaultRouter()
router.register(r"notifications", NotificationViewSet, basename="notification")

urlpatterns = router.urls
