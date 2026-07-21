from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import (
    AuditLogViewSet,
    BackupViewSet,
    ConfigurationViewSet,
    DashboardAPIView,
    NotificationViewSet,
    RoleProfileViewSet,
    RoleViewSet,
    StatisticsViewSet,
    UserViewSet,
)

app_name = "dashboard_admin"

# Create router for ViewSets
router = DefaultRouter()
router.register(r"configurations", ConfigurationViewSet, basename="configuration")
router.register(r"notifications", NotificationViewSet, basename="notification")
router.register(r"backups", BackupViewSet, basename="backup")
router.register(r"users", UserViewSet, basename="user")
router.register(r"roles", RoleViewSet, basename="role")
router.register(r"role-profiles", RoleProfileViewSet, basename="role_profile")

urlpatterns = [
    path(
        "users/bulk-delete/",
        UserViewSet.as_view({"post": "bulk_delete"}),
        name="user-bulk-delete",
    ),
    path("", include(router.urls)),
    # Dashboard overview - special case as it doesn't follow REST pattern
    path(
        "overview/",
        DashboardAPIView.as_view({"get": "overview"}),
        name="dashboard_overview",
    ),
    # Statistics - special case as APIView
    path(
        "statistics/",
        StatisticsViewSet.as_view({"get": "university"}),
        name="university_statistics",
    ),
    # Audit logs - special case as APIView
    path("audit-logs/", AuditLogViewSet.as_view({"get": "list"}), name="audit_logs"),
]
