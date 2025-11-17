from rest_framework import serializers

from services.dependent_service.dashboard_module.dashboard_shared_app.models import (
    AuditLog,
    BackupRecord,
    SystemConfiguration,
)
from services.foundational_service.auth_module.user_app.models import Role, User


class UserManagementSerializer(serializers.ModelSerializer):
    role_name = serializers.CharField(source="role.name", read_only=True)

    class Meta:
        model = User
        fields = [
            "id",
            "email",
            "first_name",
            "last_name",
            "is_active",
            "role",
            "role_name",
            "date_joined",
            "last_login",
        ]
        read_only_fields = ["id", "date_joined", "last_login"]


class RoleManagementSerializer(serializers.ModelSerializer):
    user_count = serializers.SerializerMethodField()

    class Meta:
        model = Role
        fields = ["id", "name", "description", "user_count"]
        read_only_fields = ["id"]

    def get_user_count(self, obj):
        return obj.users.count()


class SystemConfigurationSerializer(serializers.ModelSerializer):
    class Meta:
        model = SystemConfiguration
        fields = [
            "id",
            "config_type",
            "key",
            "value",
            "is_active",
            "created_by",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "created_at", "updated_at", "created_by"]


class AuditLogSerializer(serializers.ModelSerializer):
    user_email = serializers.CharField(source="user.email", read_only=True)

    class Meta:
        model = AuditLog
        fields = [
            "id",
            "user",
            "user_email",
            "action",
            "model_name",
            "object_id",
            "changes",
            "ip_address",
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
            "initiated_by",
            "initiated_by_email",
            "started_at",
            "completed_at",
            "error_message",
        ]
        read_only_fields = ["id", "started_at", "completed_at", "initiated_by"]


class SuperAdminDashboardStatsSerializer(serializers.Serializer):
    total_users = serializers.IntegerField()
    active_users = serializers.IntegerField()
    total_roles = serializers.IntegerField()
    recent_logins = serializers.IntegerField()
    system_configs = serializers.IntegerField()
    recent_backups = serializers.IntegerField()
