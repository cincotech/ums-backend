from django.contrib.auth import get_user_model
from rest_framework import serializers

from services.core_service.academic_module.faculty_app.models import Faculty
from services.core_service.academic_module.university_app.models import University
from services.dependent_service.dashboard_module.dashboard_super_admin_app.models import (
    AuditLog,
    BackupRecord,
    EmergencyRecovery,
)
from services.dependent_service.infrastructure_module.room_app.models import Room
from services.foundational_service.auth_module.authorization_app.models import Profile
from services.foundational_service.auth_module.user_app.models import Role
from services.foundational_service.geo_module.serializers import CollineSerializer

from .models import (
    UniversityConfiguration,
    UniversityNotification,
    UniversityStatistics,
)

User = get_user_model()


# ============== University Admin Models ==============
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


# ============== Super Admin Shared Models ==============
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


# ============== User Management Serializers ==============
class RoleSerializer(serializers.ModelSerializer):
    class Meta:
        model = Role
        fields = ["id", "name", "description"]
        read_only_fields = ["id"]


class ProfileSerializer(serializers.ModelSerializer):
    faculty_abreviation = serializers.CharField(
        source="faculty.faculty_abreviation", read_only=True
    )

    class Meta:
        model = Profile
        fields = ["id", "position", "start_date", "end_date", "faculty_abreviation"]
        read_only_fields = ["id"]


class UserListSerializer(serializers.ModelSerializer):
    role = RoleSerializer(read_only=True)
    nationality_name = serializers.CharField(
        read_only=True, source="nationality.country_name"
    )
    residence = CollineSerializer(many=True, read_only=True)
    profile = ProfileSerializer(source="profiles", many=True, read_only=True)

    class Meta:
        model = User
        fields = [
            "id",
            "gender",
            "email",
            "phone_number",
            "first_name",
            "last_name",
            "birth_date",
            "nationality",
            "nationality_name",
            "residence",
            "marital_status",
            "role",
            "email_verified",
            "requires_2fa",
            "requires_2fa_qr",
            "requires_2fa_email",
            "requires_2fa_static",
            "totp_secret_key",
            "profile_picture",
            "spoken_languages",
            "phone_number",
            "is_active",
            "profile",
            "created_at",
        ]
        read_only_fields = ["id", "created_at"]


class UserDetailSerializer(serializers.ModelSerializer):
    role_name = serializers.CharField(source="role.name", read_only=True)
    profile = ProfileSerializer(source="profiles", many=True, read_only=True)

    class Meta:
        model = User
        fields = [
            "id",
            "email",
            "first_name",
            "last_name",
            "phone_number",
            "birth_date",
            "gender",
            "is_active",
            "role",
            "role_name",
            "profile",
            "email_verified",
            "created_at",
            "last_login",
            "profile_picture",
        ]
        read_only_fields = ["id", "created_at", "last_login", "email_verified"]


class UserCreateSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, min_length=8)
    role_id = serializers.UUIDField(required=False, allow_null=True)

    class Meta:
        model = User
        fields = [
            "email",
            "first_name",
            "last_name",
            "password",
            "phone_number",
            "role_id",
        ]

    def create(self, validated_data):
        role_id = validated_data.pop("role_id", None)
        password = validated_data.pop("password")

        user = User.objects.create_user(password=password, **validated_data)

        if role_id:
            try:
                role = Role.objects.get(id=role_id)
                user.role = role
                user.save()
            except Role.DoesNotExist:
                pass

        return user


class UserUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ["first_name", "last_name", "phone_number", "is_active"]


class ChangePasswordSerializer(serializers.Serializer):
    new_password = serializers.CharField(write_only=True, min_length=8)
    confirm_password = serializers.CharField(write_only=True, min_length=8)

    def validate(self, data):
        if data["new_password"] != data["confirm_password"]:
            raise serializers.ValidationError("Passwords do not match")
        return data


class AssignRoleSerializer(serializers.Serializer):
    role_id = serializers.UUIDField()


class UserProfileSerializer(serializers.ModelSerializer):
    user_email = serializers.CharField(source="user.email", read_only=True)
    faculty_abreviation = serializers.CharField(
        source="faculty.faculty_abreviation", read_only=True
    )

    class Meta:
        model = Profile
        fields = [
            "id",
            "user_email",
            "position",
            "start_date",
            "end_date",
            "faculty_abreviation",
        ]
        read_only_fields = ["id"]


# ============== Role Profile Management Serializers ==============
class RoleProfileSerializer(serializers.ModelSerializer):
    room_id = serializers.UUIDField(source="room.id", read_only=True, allow_null=True)
    room_name = serializers.CharField(
        source="room.room_number", read_only=True, allow_null=True
    )
    faculty_abreviation = serializers.CharField(
        source="faculty.faculty_abreviation", read_only=True
    )

    class Meta:
        model = Profile
        fields = [
            "id",
            "position",
            "start_date",
            "end_date",
            "room_id",
            "room_name",
            "faculty_abreviation",
        ]
        read_only_fields = ["id"]


class RectorProfileSerializer(RoleProfileSerializer):
    university_id = serializers.UUIDField(
        source="university.id", read_only=True, allow_null=True
    )
    university_name = serializers.CharField(
        source="university.university_name", read_only=True, allow_null=True
    )

    class Meta:
        model = Profile
        fields = [
            "id",
            "position",
            "start_date",
            "end_date",
            "room_id",
            "room_name",
            "university_id",
            "university_name",
        ]
        read_only_fields = ["id"]


class DeanProfileSerializer(RoleProfileSerializer):
    faculty_id = serializers.UUIDField(
        source="faculty.id", read_only=True, allow_null=True
    )
    faculty_name = serializers.CharField(
        source="faculty.faculty_name", read_only=True, allow_null=True
    )

    class Meta:
        model = Profile
        fields = [
            "id",
            "position",
            "start_date",
            "end_date",
            "room_id",
            "room_name",
            "faculty_id",
            "faculty_name",
        ]
        read_only_fields = ["id"]


class CreateRoleProfileSerializer(serializers.Serializer):
    position = serializers.CharField(max_length=100, required=True)
    start_date = serializers.DateField(required=True)
    end_date = serializers.DateField(required=False, allow_null=True)
    room_id = serializers.UUIDField(required=False, allow_null=True)
    university_id = serializers.UUIDField(required=False, allow_null=True)
    faculty_id = serializers.UUIDField(required=False, allow_null=True)

    def validate_room_id(self, value):
        if value and not Room.objects.filter(id=value).exists():
            raise serializers.ValidationError("Room not found")
        return value

    def validate_university_id(self, value):
        if value and not University.objects.filter(id=value).exists():
            raise serializers.ValidationError("University not found")
        return value

    def validate_faculty_id(self, value):
        if value and not Faculty.objects.filter(id=value).exists():
            raise serializers.ValidationError("Faculty not found")
        return value


class CreateUserWithProfileSerializer(serializers.Serializer):
    email = serializers.EmailField()
    first_name = serializers.CharField(max_length=150)
    last_name = serializers.CharField(max_length=150)
    password = serializers.CharField(write_only=True, min_length=8)

    role_id = serializers.UUIDField()  # 🔥 UUID instead of name

    position = serializers.CharField(max_length=100)
    start_date = serializers.DateField()
    end_date = serializers.DateField(required=False, allow_null=True)

    room_id = serializers.UUIDField(required=False, allow_null=True)
    university_id = serializers.UUIDField(required=False, allow_null=True)
    faculty_id = serializers.UUIDField(required=False, allow_null=True)


class RoleWithFieldsSerializer(serializers.Serializer):
    id = serializers.UUIDField()
    name = serializers.CharField()
    description = serializers.CharField()
    fields = serializers.DictField()
