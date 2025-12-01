from datetime import timedelta

from django.utils import timezone
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.token_blacklist.models import (
    BlacklistedToken,
    OutstandingToken,
)

from core.audit import log_security_event, log_user_action
from core.response_handler import error_response, success_response
from services.dependent_service.dashboard_module.dashboard_super_admin_app.models import (
    AuditLog,
)

from .backup_service import SecureBackupService
from .models import UniversityConfiguration, UniversityNotification
from .serializers import (
    AuditLogSerializer,
    BackupRecordSerializer,
    EmergencyRecoverySerializer,
    UniversityConfigurationSerializer,
    UniversityNotificationSerializer,
    UniversityStatisticsSerializer,
)
from .services import ConfigurationService, UniversityAdminService


def get_admin_university(request):
    """Extract university from admin profile"""
    try:
        return request.user.university
    except AttributeError:
        return None


# ============== Dashboard Overview ==============
@api_view(["GET"])
@permission_classes([IsAuthenticated])
def dashboard_overview(request):
    """Get admin dashboard overview with all statistics"""
    try:
        university = get_admin_university(request)
        if not university:
            return error_response(
                message="University not found",
                status_code=status.HTTP_403_FORBIDDEN,
            )

        stats = UniversityAdminService.update_university_statistics(university)

        pending_notifications = UniversityNotification.objects.filter(
            recipient=request.user, is_read=False
        ).count()

        recent_logs = AuditLog.objects.filter(
            university=university, timestamp__gte=timezone.now() - timedelta(days=7)
        ).count()

        active_tokens = OutstandingToken.objects.filter(
            expires_at__gt=timezone.now()
        ).exclude(id__in=BlacklistedToken.objects.values_list("token_id", flat=True))

        # Count unique users
        active_users_count = (
            active_tokens.values_list("user", flat=True).distinct().count()
        )

        data = UniversityStatisticsSerializer(stats).data
        data["pending_notifications"] = pending_notifications
        data["recent_activities"] = recent_logs
        data["active_users"] = active_users_count

        log_user_action(
            request,
            "view",
            "Accessed dashboard overview",
            "Dashboard",
            str(university.id),
        )
        return success_response(
            data=data, message="Dashboard overview retrieved successfully"
        )
    except Exception as e:
        log_security_event(
            request,
            "view",
            f"Dashboard access failed: {str(e)}",
            severity="error",
            success=False,
        )
        return error_response(
            message=f"Error retrieving dashboard: {str(e)}",
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )


# ============== Configuration Management ==============
@api_view(["GET", "POST"])
@permission_classes([IsAuthenticated])
def configuration_list(request):
    """List all configurations or create new one"""
    try:
        university = get_admin_university(request)
        if not university:
            return error_response(
                message="University not found",
                status_code=status.HTTP_403_FORBIDDEN,
            )

        if request.method == "GET":
            category = request.query_params.get("category")

            if category:
                configs = ConfigurationService.get_category_configs(
                    university, category
                )
            else:
                configs = ConfigurationService.get_all_configs(university)

            serializer = UniversityConfigurationSerializer(configs, many=True)
            log_user_action(
                request,
                "view",
                "Listed configurations",
                "UniversityConfiguration",
                str(university.id),
            )
            return success_response(
                data=serializer.data, message="Configurations retrieved successfully"
            )

        elif request.method == "POST":
            serializer = UniversityConfigurationSerializer(data=request.data)
            if serializer.is_valid():
                config = serializer.save(university=university, created_by=request.user)
                log_user_action(
                    request,
                    "create",
                    f"Created configuration: {config.key}",
                    "UniversityConfiguration",
                    str(config.id),
                    {"category": config.category, "key": config.key},
                )
                result_serializer = UniversityConfigurationSerializer(config)
                return success_response(
                    data=result_serializer.data,
                    message="Configuration created successfully",
                    status_code=status.HTTP_201_CREATED,
                )
            return error_response(
                message="Validation error",
                errors=serializer.errors,
                status_code=status.HTTP_400_BAD_REQUEST,
            )
    except Exception as e:
        log_security_event(
            request,
            "create",
            f"Configuration operation failed: {str(e)}",
            severity="error",
            success=False,
        )
        return error_response(
            message=f"Error: {str(e)}",
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )


@api_view(["GET", "PUT", "DELETE"])
@permission_classes([IsAuthenticated])
def configuration_detail(request, config_id):
    """Get, update, or delete a configuration"""
    try:
        university = get_admin_university(request)
        if not university:
            return error_response(
                message="University not found",
                status_code=status.HTTP_403_FORBIDDEN,
            )

        config = UniversityConfiguration.objects.get(
            id=config_id, university=university
        )

        if request.method == "GET":
            serializer = UniversityConfigurationSerializer(config)
            log_user_action(
                request,
                "view",
                f"Viewed configuration: {config.key}",
                "UniversityConfiguration",
                str(config.id),
            )
            return success_response(
                data=serializer.data, message="Configuration retrieved successfully"
            )

        elif request.method == "PUT":
            old_value = config.value
            serializer = UniversityConfigurationSerializer(
                config, data=request.data, partial=True
            )
            if serializer.is_valid():
                config = serializer.save(modified_by=request.user)
                log_user_action(
                    request,
                    "update",
                    f"Updated configuration: {config.key}",
                    "UniversityConfiguration",
                    str(config.id),
                    {"old_value": old_value, "new_value": config.value},
                )
                result_serializer = UniversityConfigurationSerializer(config)
                return success_response(
                    data=result_serializer.data,
                    message="Configuration updated successfully",
                )
            return error_response(
                message="Validation error",
                errors=serializer.errors,
                status_code=status.HTTP_400_BAD_REQUEST,
            )

        elif request.method == "DELETE":
            config_key = config.key
            config.delete()
            log_user_action(
                request,
                "delete",
                f"Deleted configuration: {config_key}",
                "UniversityConfiguration",
                str(config_id),
            )
            return success_response(message="Configuration deleted successfully")

    except UniversityConfiguration.DoesNotExist:
        return error_response(
            message="Configuration not found", status_code=status.HTTP_404_NOT_FOUND
        )
    except Exception as e:
        log_security_event(
            request,
            "update",
            f"Configuration operation failed: {str(e)}",
            severity="error",
            success=False,
        )
        return error_response(
            message=f"Error: {str(e)}",
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )


# ============== Statistics ==============
@api_view(["GET"])
@permission_classes([IsAuthenticated])
def university_statistics(request):
    """Get detailed statistics for university"""
    try:
        university = get_admin_university(request)
        if not university:
            return error_response(
                message="University not found",
                status_code=status.HTTP_403_FORBIDDEN,
            )

        stats = UniversityAdminService.update_university_statistics(university)
        serializer = UniversityStatisticsSerializer(stats)
        log_user_action(
            request,
            "view",
            "Viewed university statistics",
            "UniversityStatistics",
            str(stats.id),
        )
        return success_response(
            data=serializer.data, message="University statistics retrieved successfully"
        )
    except Exception as e:
        log_security_event(
            request,
            "view",
            f"Statistics access failed: {str(e)}",
            severity="error",
            success=False,
        )
        return error_response(
            message=f"Error: {str(e)}",
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )


# ============== Notifications ==============
@api_view(["GET"])
@permission_classes([IsAuthenticated])
def notification_list(request):
    """Get notifications for admin"""
    try:
        notifications = UniversityNotification.objects.filter(
            recipient=request.user
        ).order_by("-created_at")[:50]

        serializer = UniversityNotificationSerializer(notifications, many=True)
        return success_response(
            data=serializer.data, message="Notifications retrieved successfully"
        )
    except Exception as e:
        return error_response(
            message=f"Error: {str(e)}",
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )


@api_view(["POST"])
@permission_classes([IsAuthenticated])
def mark_notification_read(request, notification_id):
    """Mark notification as read"""
    try:
        notification = UniversityNotification.objects.get(
            id=notification_id, recipient=request.user
        )
        notification.mark_as_read()
        log_user_action(
            request,
            "update",
            "Marked notification as read",
            "UniversityNotification",
            str(notification_id),
        )
        return success_response(message="Notification marked as read")
    except UniversityNotification.DoesNotExist:
        return error_response(
            message="Notification not found", status_code=status.HTTP_404_NOT_FOUND
        )
    except Exception as e:
        return error_response(
            message=f"Error: {str(e)}",
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )


# ============== Audit Logs ==============
@api_view(["GET"])
@permission_classes([IsAuthenticated])
def audit_logs(request):
    """Get audit logs for university"""
    try:
        university = get_admin_university(request)
        if not university:
            return error_response(
                message="University not found",
                status_code=status.HTTP_403_FORBIDDEN,
            )

        days = int(request.query_params.get("days", 7))
        timezone.now() - timedelta(days=days)

        # logs = AuditLog.objects.filter(
        #     university=university,
        #     timestamp__gte=start_date
        # ).order_by("-timestamp")[:100]

        logs = AuditLog.objects.all()
        serializer = AuditLogSerializer(logs, many=True)
        return success_response(
            data=serializer.data, message="Audit logs retrieved successfully"
        )
    except Exception as e:
        return error_response(
            message=f"Error: {str(e)}",
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )


# ============== Backup & Restore ==============
@api_view(["GET", "POST"])
@permission_classes([IsAuthenticated])
def backup_list(request):
    """List backups or create new backup"""
    try:
        university = get_admin_university(request)
        if not university:
            return error_response(
                message="University not found",
                status_code=status.HTTP_403_FORBIDDEN,
            )

        if request.method == "GET":
            backups = SecureBackupService.get_university_backups(university)
            serializer = BackupRecordSerializer(backups, many=True)
            return success_response(
                data=serializer.data, message="Backups retrieved successfully"
            )

        elif request.method == "POST":
            backup = SecureBackupService.create_backup(university, request.user)
            log_user_action(
                request,
                "create",
                f"Created encrypted backup for {university.university_name}",
                "BackupRecord",
                str(backup.id),
            )
            serializer = BackupRecordSerializer(backup)
            return success_response(
                data=serializer.data,
                message="Backup created successfully",
                status_code=status.HTTP_201_CREATED,
            )
    except Exception as e:
        log_security_event(
            request,
            "create",
            f"Backup creation failed: {str(e)}",
            severity="error",
            success=False,
        )
        return error_response(
            message=f"Error: {str(e)}",
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )


@api_view(["POST"])
@permission_classes([IsAuthenticated])
def restore_backup(request, backup_id):
    """Restore from backup"""
    try:
        university = get_admin_university(request)
        if not university:
            return error_response(
                message="University not found",
                status_code=status.HTTP_403_FORBIDDEN,
            )

        from services.dependent_service.dashboard_module.dashboard_super_admin_app.models import (
            BackupRecord,
        )

        backup = BackupRecord.objects.get(
            id=backup_id, metadata__university_id=str(university.id)
        )

        recovery = SecureBackupService.restore_backup(backup, request.user)
        log_user_action(
            request,
            "update",
            f"Restored data from backup {backup_id}",
            "EmergencyRecovery",
            str(recovery.id),
        )

        serializer = EmergencyRecoverySerializer(recovery)
        return success_response(
            data=serializer.data, message="Backup restored successfully"
        )
    except Exception as e:
        log_security_event(
            request,
            "update",
            f"Restore failed: {str(e)}",
            severity="error",
            success=False,
        )
        return error_response(
            message=f"Error: {str(e)}",
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )


@api_view(["DELETE"])
@permission_classes([IsAuthenticated])
def delete_backup(request, backup_id):
    """Delete backup securely"""
    try:
        university = get_admin_university(request)
        if not university:
            return error_response(
                message="University not found",
                status_code=status.HTTP_403_FORBIDDEN,
            )

        from services.dependent_service.dashboard_module.dashboard_super_admin_app.models import (
            BackupRecord,
        )

        backup = BackupRecord.objects.get(
            id=backup_id, metadata__university_id=str(university.id)
        )

        SecureBackupService.delete_backup(backup)
        log_user_action(
            request,
            "delete",
            f"Deleted backup {backup_id}",
            "BackupRecord",
            str(backup_id),
        )

        return success_response(message="Backup deleted successfully")
    except Exception as e:
        log_security_event(
            request,
            "delete",
            f"Backup deletion failed: {str(e)}",
            severity="error",
            success=False,
        )
        return error_response(
            message=f"Error: {str(e)}",
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )
