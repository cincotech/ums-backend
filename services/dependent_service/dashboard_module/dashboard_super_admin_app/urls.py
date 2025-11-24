# from django.urls import path

# from . import views

# urlpatterns = [
#     path(
#         "super-admin/overview/",
#         views.super_admin_dashboard_overview,
#         name="super-admin-overview",
#     ),
#     path("super-admin/users/", views.user_management, name="user-management"),
#     path(
#         "super-admin/users/<uuid:user_id>/",
#         views.user_management_detail,
#         name="user-management-detail",
#     ),
#     path("super-admin/roles/", views.role_management, name="role-management"),
#     path(
#         "super-admin/roles/<uuid:role_id>/",
#         views.role_management_detail,
#         name="role-management-detail",
#     ),
#     path(
#         "super-admin/config/", views.system_configuration, name="system-configuration"
#     ),
#     path(
#         "super-admin/config/<uuid:config_id>/",
#         views.system_configuration_detail,
#         name="system-configuration-detail",
#     ),
#     path(
#         "super-admin/users/<uuid:user_id>/reset-password/",
#         views.reset_user_password,
#         name="reset-user-password",
#     ),
#     path("super-admin/backup/", views.initiate_backup, name="initiate-backup"),
#     path("super-admin/backup/history/", views.backup_history, name="backup-history"),
#     path("super-admin/audit-logs/", views.audit_logs, name="audit-logs"),
# ]
