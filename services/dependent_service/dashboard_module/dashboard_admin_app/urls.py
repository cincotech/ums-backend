from django.urls import path

from . import role_profile_views, user_views, views

app_name = "dashboard_admin"

urlpatterns = [
    # Dashboard
    path("overview/", views.dashboard_overview, name="dashboard_overview"),
    # Configuration
    path("configurations/", views.configuration_list, name="configuration_list"),
    path(
        "configurations/<uuid:config_id>/",
        views.configuration_detail,
        name="configuration_detail",
    ),
    # Statistics
    path("statistics/", views.university_statistics, name="university_statistics"),
    # Notifications
    path("notifications/", views.notification_list, name="notification_list"),
    path(
        "notifications/<uuid:notification_id>/read/",
        views.mark_notification_read,
        name="mark_notification_read",
    ),
    # Audit Logs
    path("audit-logs/", views.audit_logs, name="audit_logs"),
    # Backup & Restore
    path("backups/", views.backup_list, name="backup_list"),
    path(
        "backups/<uuid:backup_id>/restore/", views.restore_backup, name="restore_backup"
    ),
    path("backups/<uuid:backup_id>/", views.delete_backup, name="delete_backup"),
    # User Management
    path("users/", user_views.user_list, name="user_list"),
    path("users/<uuid:user_id>/", user_views.user_detail, name="user_detail"),
    path(
        "users/<uuid:user_id>/password/",
        user_views.change_user_password,
        name="change_user_password",
    ),
    path(
        "users/<uuid:user_id>/role/",
        user_views.assign_user_role,
        name="assign_user_role",
    ),
    path("users/<uuid:user_id>/profile/", user_views.user_profile, name="user_profile"),
    path(
        "users/<uuid:user_id>/deactivate/",
        user_views.deactivate_user,
        name="deactivate_user",
    ),
    path(
        "users/<uuid:user_id>/activate/", user_views.activate_user, name="activate_user"
    ),
    # Roles
    path("roles/", user_views.role_list, name="role_list"),
    # Role-Specific User & Profile Management
    path("roles/fields/", role_profile_views.role_fields_info, name="role_fields_info"),
    path(
        "users/create-with-profile/",
        role_profile_views.create_user_with_profile,
        name="create_user_with_profile",
    ),
    path(
        "users/<uuid:user_id>/profile-detail/",
        role_profile_views.get_user_profile,
        name="get_user_profile",
    ),
    path(
        "users/<uuid:user_id>/profile-update/",
        role_profile_views.update_user_profile,
        name="update_user_profile",
    ),
]
