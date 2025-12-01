from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import SuperAdminDashboardViewSet

router = DefaultRouter()
router.register(
    r"dashboard", SuperAdminDashboardViewSet, basename="super-admin-dashboard"
)

urlpatterns = [
    path("", include(router.urls)),
]
