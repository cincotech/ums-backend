from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated

from core.response_handler import error_response, success_response
from services.dependent_service.dashboard_module.dashboard_shared_app.models import (
    BackupRecord,
    SystemConfiguration,
)
from services.foundational_service.auth_module.user_app.models import Role, User

from .serializers import (
    AuditLogSerializer,
    BackupRecordSerializer,
    RoleManagementSerializer,
    SuperAdminDashboardStatsSerializer,
    SystemConfigurationSerializer,
    UserManagementSerializer,
)
from .services import SuperAdminDashboardService


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def super_admin_dashboard_overview(request):
    """Get super admin dashboard overview"""
    try:
        stats = SuperAdminDashboardService.get_dashboard_stats()
        serializer = SuperAdminDashboardStatsSerializer(stats)
        return success_response(
            data=serializer.data, message="Dashboard overview retrieved"
        )
    except Exception as e:
        return error_response(
            message=f"Error: {str(e)}",
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )


@api_view(["GET", "POST"])
@permission_classes([IsAuthenticated])
def user_management(request):
    """Manage users - list all or create new"""
    try:
        if request.method == "GET":
            users = User.objects.all().select_related("role")
            serializer = UserManagementSerializer(users, many=True)
            return success_response(data=serializer.data, message="Users retrieved")

        elif request.method == "POST":
            user = SuperAdminDashboardService.manage_user(
                None, "create", request.data, request.user
            )
            serializer = UserManagementSerializer(user)
            return success_response(data=serializer.data, message="User created")
    except Exception as e:
        return error_response(
            message=f"Error: {str(e)}",
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )


@api_view(["PUT", "DELETE", "PATCH"])
@permission_classes([IsAuthenticated])
def user_management_detail(request, user_id):
    """Update, delete or toggle user status"""
    try:
        if request.method == "PUT":
            user = SuperAdminDashboardService.manage_user(
                user_id, "update", request.data, request.user
            )
            serializer = UserManagementSerializer(user)
            return success_response(data=serializer.data, message="User updated")

        elif request.method == "PATCH":
            user = SuperAdminDashboardService.manage_user(
                user_id, "toggle_active", {}, request.user
            )
            serializer = UserManagementSerializer(user)
            return success_response(data=serializer.data, message="User status toggled")

        elif request.method == "DELETE":
            SuperAdminDashboardService.manage_user(user_id, "delete", {}, request.user)
            return success_response(message="User deleted")
    except Exception as e:
        return error_response(
            message=f"Error: {str(e)}",
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )


@api_view(["GET", "POST"])
@permission_classes([IsAuthenticated])
def role_management(request):
    """Manage roles - list all or create new"""
    try:
        if request.method == "GET":
            roles = Role.objects.all()
            serializer = RoleManagementSerializer(roles, many=True)
            return success_response(data=serializer.data, message="Roles retrieved")

        elif request.method == "POST":
            role = SuperAdminDashboardService.manage_role(
                None, "create", request.data, request.user
            )
            serializer = RoleManagementSerializer(role)
            return success_response(data=serializer.data, message="Role created")
    except Exception as e:
        return error_response(
            message=f"Error: {str(e)}",
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )


@api_view(["PUT", "DELETE"])
@permission_classes([IsAuthenticated])
def role_management_detail(request, role_id):
    """Update or delete role"""
    try:
        if request.method == "PUT":
            role = SuperAdminDashboardService.manage_role(
                role_id, "update", request.data, request.user
            )
            serializer = RoleManagementSerializer(role)
            return success_response(data=serializer.data, message="Role updated")

        elif request.method == "DELETE":
            SuperAdminDashboardService.manage_role(role_id, "delete", {}, request.user)
            return success_response(message="Role deleted")
    except Exception as e:
        return error_response(
            message=f"Error: {str(e)}",
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )


@api_view(["GET", "POST"])
@permission_classes([IsAuthenticated])
def system_configuration(request):
    """Manage system configurations"""
    try:
        if request.method == "GET":
            configs = SystemConfiguration.objects.filter(is_active=True)
            serializer = SystemConfigurationSerializer(configs, many=True)
            return success_response(
                data=serializer.data, message="Configurations retrieved"
            )

        elif request.method == "POST":
            config = SuperAdminDashboardService.manage_system_config(
                None, "create", request.data, request.user
            )
            serializer = SystemConfigurationSerializer(config)
            return success_response(
                data=serializer.data, message="Configuration created"
            )
    except Exception as e:
        return error_response(
            message=f"Error: {str(e)}",
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )


@api_view(["PUT", "DELETE"])
@permission_classes([IsAuthenticated])
def system_configuration_detail(request, config_id):
    """Update or delete system configuration"""
    try:
        if request.method == "PUT":
            config = SuperAdminDashboardService.manage_system_config(
                config_id, "update", request.data, request.user
            )
            serializer = SystemConfigurationSerializer(config)
            return success_response(
                data=serializer.data, message="Configuration updated"
            )

        elif request.method == "DELETE":
            SuperAdminDashboardService.manage_system_config(
                config_id, "delete", {}, request.user
            )
            return success_response(message="Configuration deleted")
    except Exception as e:
        return error_response(
            message=f"Error: {str(e)}",
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )


@api_view(["POST"])
@permission_classes([IsAuthenticated])
def reset_user_password(request, user_id):
    """Reset user password (emergency function)"""
    try:
        new_password = request.data.get("new_password")
        if not new_password:
            return error_response(
                message="New password required", status_code=status.HTTP_400_BAD_REQUEST
            )

        SuperAdminDashboardService.reset_user_password(
            user_id, new_password, request.user
        )
        return success_response(message="Password reset successfully")
    except Exception as e:
        return error_response(
            message=f"Error: {str(e)}",
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )


@api_view(["POST"])
@permission_classes([IsAuthenticated])
def initiate_backup(request):
    """Initiate database backup"""
    try:
        backup_type = request.data.get("backup_type", "full")
        backup = SuperAdminDashboardService.initiate_backup(backup_type, request.user)
        serializer = BackupRecordSerializer(backup)
        return success_response(data=serializer.data, message="Backup initiated")
    except Exception as e:
        return error_response(
            message=f"Error: {str(e)}",
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def backup_history(request):
    """Get backup history"""
    try:
        backups = BackupRecord.objects.all().order_by("-started_at")[:20]
        serializer = BackupRecordSerializer(backups, many=True)
        return success_response(
            data=serializer.data, message="Backup history retrieved"
        )
    except Exception as e:
        return error_response(
            message=f"Error: {str(e)}",
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def audit_logs(request):
    """Get audit logs for monitoring"""
    try:
        logs = SuperAdminDashboardService.get_audit_logs()
        serializer = AuditLogSerializer(logs, many=True)
        return success_response(data=serializer.data, message="Audit logs retrieved")
    except Exception as e:
        return error_response(
            message=f"Error: {str(e)}",
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )
