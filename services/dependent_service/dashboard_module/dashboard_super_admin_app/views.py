from datetime import timedelta

from django.utils import timezone
from django.db.models import Q
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import OrderingFilter, SearchFilter
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from core.audit import log_audit, log_backup_action, log_config_change
from services.core_service.academic_module.university_app.models import University
from services.foundational_service.auth_module.user_app.models import User

from .models import AuditLog, BackupRecord, EmergencyRecovery, SystemConfiguration
from .permissions import IsSuperAdmin
from .serializers import (
    AuditLogSerializer,
    BackupRecordSerializer,
    EmergencyRecoverySerializer,
    SystemConfigurationSerializer,
)


class SuperAdminDashboardViewSet(viewsets.ViewSet):
    """Super Admin Dashboard - Full system management"""

    permission_classes = [IsAuthenticated, IsSuperAdmin]

    @action(detail=False, methods=["get"])
    def overview(self, request):
        """System overview statistics"""
        data = {
            "total_universities": University.objects.count(),
            "total_users": User.objects.count(),
            "active_users": User.objects.filter(is_active=True).count(),
            "inactive_users": User.objects.filter(is_active=False).count(),
            "failed_logins_24h": AuditLog.objects.filter(
                action="failed_login",
                timestamp__gte=timezone.now() - timedelta(hours=24),
            ).count(),
            "security_alerts_24h": AuditLog.objects.filter(
                severity__in=["warning", "critical"],
                timestamp__gte=timezone.now() - timedelta(hours=24),
            ).count(),
            "pending_backups": BackupRecord.objects.filter(status="pending").count(),
            "completed_backups_24h": BackupRecord.objects.filter(
                status="completed",
                completed_at__gte=timezone.now() - timedelta(hours=24),
            ).count(),
        }
        return Response(data, status=status.HTTP_200_OK)

    @action(detail=False, methods=["get"])
    def system_health(self, request):
        """System health metrics"""
        data = {
            "database_status": "healthy",
            "backup_running": BackupRecord.objects.filter(status="running").exists(),
            "security_alerts": AuditLog.objects.filter(
                severity__in=["warning", "critical"],
                timestamp__gte=timezone.now() - timedelta(hours=24),
            ).count(),
            "active_sessions": User.objects.filter(is_active=True).count(),
            "failed_operations_24h": AuditLog.objects.filter(
                success=False,
                timestamp__gte=timezone.now() - timedelta(hours=24),
            ).count(),
        }
        return Response(data, status=status.HTTP_200_OK)

    @action(detail=False, methods=["get"])
    def audit_logs(self, request):
        """Get audit logs with filtering"""
        action_filter = request.query_params.get("action")
        severity_filter = request.query_params.get("severity")
        days = int(request.query_params.get("days", 7))

        logs = AuditLog.objects.filter(
            timestamp__gte=timezone.now() - timedelta(days=days)
        )

        if action_filter:
            logs = logs.filter(action=action_filter)
        if severity_filter:
            logs = logs.filter(severity=severity_filter)

        logs = logs[:100]
        serializer = AuditLogSerializer(logs, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @action(detail=False, methods=["get"])
    def backups(self, request):
        """Get backup records"""
        backups = BackupRecord.objects.all()[:20]
        serializer = BackupRecordSerializer(backups, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @action(detail=False, methods=["post"])
    def initiate_backup(self, request):
        """Initiate system backup"""
        backup_type = request.data.get("backup_type", "full")

        backup = BackupRecord.objects.create(
            backup_type=backup_type,
            initiated_by=request.user,
            status="pending",
        )

        log_backup_action(request, str(backup.id), "initiated", "pending")

        serializer = BackupRecordSerializer(backup)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    @action(detail=False, methods=["get"])
    def system_config(self, request):
        """Get system configurations"""
        configs = SystemConfiguration.objects.filter(is_active=True)
        serializer = SystemConfigurationSerializer(configs, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @action(detail=False, methods=["post"])
    def update_system_config(self, request):
        """Update system configuration"""
        category = request.data.get("category")
        key = request.data.get("key")
        value = request.data.get("value")

        config, created = SystemConfiguration.objects.get_or_create(
            category=category,
            key=key,
            defaults={"created_by": request.user},
        )

        old_value = config.value
        config.value = value
        config.modified_by = request.user
        config.save()

        log_config_change(request, category, key, old_value, value)

        serializer = SystemConfigurationSerializer(config)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @action(detail=False, methods=["get"])
    def emergency_recoveries(self, request):
        """Get emergency recovery records"""
        recoveries = EmergencyRecovery.objects.all()[:20]
        serializer = EmergencyRecoverySerializer(recoveries, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @action(detail=False, methods=["post"])
    def initiate_recovery(self, request):
        """Initiate emergency recovery"""
        recovery_type = request.data.get("recovery_type")
        target_user_id = request.data.get("target_user_id")
        reason = request.data.get("reason")

        try:
            target_user = (
                User.objects.get(id=target_user_id) if target_user_id else None
            )
        except User.DoesNotExist:
            return Response(
                {"error": "Target user not found"},
                status=status.HTTP_404_NOT_FOUND,
            )

        recovery = EmergencyRecovery.objects.create(
            recovery_type=recovery_type,
            target_user=target_user,
            performed_by=request.user,
            reason=reason,
            status="pending",
        )

        log_audit(
            user=request.user,
            action="password_reset" if recovery_type == "password_reset" else "update",
            description=f"Emergency recovery initiated: {recovery_type}",
            entity_type="EmergencyRecovery",
            entity_id=str(recovery.id),
            request=request,
        )

        serializer = EmergencyRecoverySerializer(recovery)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    @action(detail=False, methods=["get"])
    def security_summary(self, request):
        """Get security summary"""
        days = int(request.query_params.get("days", 7))
        start_date = timezone.now() - timedelta(days=days)

        data = {
            "total_events": AuditLog.objects.filter(timestamp__gte=start_date).count(),
            "failed_logins": AuditLog.objects.filter(
                action="failed_login",
                timestamp__gte=start_date,
            ).count(),
            "account_lockouts": AuditLog.objects.filter(
                action="account_locked",
                timestamp__gte=start_date,
            ).count(),
            "security_breaches": AuditLog.objects.filter(
                action="security_breach",
                timestamp__gte=start_date,
            ).count(),
            "config_changes": AuditLog.objects.filter(
                action="config_change",
                timestamp__gte=start_date,
            ).count(),
            "role_changes": AuditLog.objects.filter(
                action="role_change",
                timestamp__gte=start_date,
            ).count(),
        }
        return Response(data, status=status.HTTP_200_OK)
