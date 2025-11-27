from rest_framework import serializers

from services.dependent_service.dashboard_module.dashboard_super_admin_app.models import (
    AuditLog,
    BackupRecord,
    EmergencyRecovery,
)

from .models import (
    UniversityConfiguration,
    UniversityNotification,
    UniversityStatistics,
)


class UniversityConfigurationSerializer(serializers.ModelSerializer):
    university_name = serializers.CharField(
        source="university.university_name", read_only=True
    )
    created_by_email = serializers.CharField(source="created_by.email", read_only=True)
    modified_by_email = serializers.CharField(
        source="modified_by.email", read_only=True, allow_null=True
    )

    class Meta:
        model = UniversityConfiguration
        fields = [
            "id",
            "university",
            "university_name",
            "category",
            "key",
            "value",
            "description",
            "is_active",
            "created_by_email",
            "modified_by_email",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "created_at", "updated_at"]


class UniversityStatisticsSerializer(serializers.ModelSerializer):
    university_name = serializers.CharField(
        source="university.university_name", read_only=True
    )

    class Meta:
        model = UniversityStatistics
        fields = [
            "id",
            "university",
            "university_name",
            "total_students",
            "total_teachers",
            "total_faculties",
            "total_departments",
            "total_courses",
            "active_enrollments",
            "pending_payments",
            "completed_exams",
            "pending_document_requests",
            "calculated_at",
        ]
        read_only_fields = ["id", "calculated_at"]


class UniversityNotificationSerializer(serializers.ModelSerializer):
    university_name = serializers.CharField(
        source="university.university_name", read_only=True, allow_null=True
    )
    recipient_email = serializers.CharField(source="recipient.email", read_only=True)

    class Meta:
        model = UniversityNotification
        fields = [
            "id",
            "university",
            "university_name",
            "recipient",
            "recipient_email",
            "notification_type",
            "priority",
            "title",
            "message",
            "action_url",
            "is_read",
            "read_at",
            "created_at",
        ]
        read_only_fields = ["id", "created_at", "read_at"]


class AuditLogSerializer(serializers.ModelSerializer):
    """Shared audit log serializer for university-level activities"""

    user_email = serializers.CharField(
        source="user.email", read_only=True, allow_null=True
    )

    class Meta:
        model = AuditLog
        fields = [
            "id",
            "user_email",
            "action",
            "severity",
            "entity_type",
            "entity_id",
            "description",
            "changes",
            "ip_address",
            "user_agent",
            "success",
            "error_message",
            "timestamp",
        ]
        read_only_fields = ["id", "timestamp"]


class BackupRecordSerializer(serializers.ModelSerializer):
    initiated_by_email = serializers.CharField(
        source="initiated_by.email", read_only=True
    )

    class Meta:
        model = BackupRecord
        fields = [
            "id",
            "backup_type",
            "status",
            "file_path",
            "file_size",
            "initiated_by_email",
            "started_at",
            "completed_at",
            "error_message",
        ]
        read_only_fields = ["id", "started_at", "completed_at"]


class EmergencyRecoverySerializer(serializers.ModelSerializer):
    performed_by_email = serializers.CharField(
        source="performed_by.email", read_only=True
    )

    class Meta:
        model = EmergencyRecovery
        fields = [
            "id",
            "recovery_type",
            "status",
            "reason",
            "result",
            "performed_by_email",
            "initiated_at",
            "completed_at",
        ]
        read_only_fields = ["id", "initiated_at", "completed_at"]


class DashboardStatsSerializer(serializers.Serializer):
    """Dashboard overview statistics for University Admin"""

    total_students = serializers.IntegerField()
    total_teachers = serializers.IntegerField()
    total_faculties = serializers.IntegerField()
    total_departments = serializers.IntegerField()
    active_enrollments = serializers.IntegerField()
    pending_payments = serializers.DecimalField(max_digits=15, decimal_places=2)
    pending_document_requests = serializers.IntegerField()
