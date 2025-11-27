from rest_framework import serializers

from .models import AuditLog, BackupRecord, EmergencyRecovery, SystemConfiguration


class SystemConfigurationSerializer(serializers.ModelSerializer):
    created_by_email = serializers.CharField(source="created_by.email", read_only=True)
    modified_by_email = serializers.CharField(
        source="modified_by.email", read_only=True, allow_null=True
    )

    class Meta:
        model = SystemConfiguration
        fields = [
            "id",
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


class AuditLogSerializer(serializers.ModelSerializer):
    user_email = serializers.CharField(
        source="user.email", read_only=True, allow_null=True
    )
    university_name = serializers.CharField(
        source="university.university_name", read_only=True, allow_null=True
    )

    class Meta:
        model = AuditLog
        fields = [
            "id",
            "user_email",
            "university_name",
            "action",
            "severity",
            "entity_type",
            "entity_id",
            "description",
            "changes",
            "ip_address",
            "user_agent",
            "location",
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
            "backup_location",
            "initiated_by_email",
            "started_at",
            "completed_at",
            "error_message",
            "metadata",
        ]
        read_only_fields = ["id", "started_at"]


class EmergencyRecoverySerializer(serializers.ModelSerializer):
    target_user_email = serializers.CharField(
        source="target_user.email", read_only=True, allow_null=True
    )
    performed_by_email = serializers.CharField(
        source="performed_by.email", read_only=True
    )

    class Meta:
        model = EmergencyRecovery
        fields = [
            "id",
            "recovery_type",
            "target_user_email",
            "performed_by_email",
            "status",
            "reason",
            "details",
            "result",
            "initiated_at",
            "completed_at",
        ]
        read_only_fields = ["id", "initiated_at"]
