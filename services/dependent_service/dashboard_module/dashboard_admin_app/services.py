import json
import os
from io import StringIO

from cryptography.fernet import Fernet
from django.contrib.auth import get_user_model
from django.core import serializers as django_serializers
from django.core.management import call_command
from django.utils import timezone

from services.core_service.academic_module.course_app.models import Course
from services.core_service.academic_module.department_app.models import Department
from services.core_service.academic_module.faculty_app.models import Faculty
from services.core_service.academic_module.teacher_app.models import Teacher
from services.core_service.academic_module.university_app.models import University
from services.core_service.student_module.inscription_app.models import Inscription
from services.core_service.student_module.student_profile_app.models import Student
from services.dependent_service.dashboard_module.dashboard_super_admin_app.models import (
    AuditLog,
    BackupRecord,
    EmergencyRecovery,
)
from services.dependent_service.document_module.request_app.models import Request
from services.dependent_service.exam_module.exam_app.models import Exam
from services.dependent_service.infrastructure_module.room_app.models import Room
from services.foundational_service.auth_module.authorization_app.models import Profile
from services.foundational_service.auth_module.user_app.models import Role

from .models import (
    UniversityConfiguration,
    UniversityNotification,
    UniversityStatistics,
)

User = get_user_model()

ROLE_PROFILE_MAPPING = {
    "rector": {
        "model": "Rector",
        "fields": ["university", "position", "room", "start_date", "end_date"],
    },
    "dean": {
        "model": "Dean",
        "fields": ["faculty", "position", "room", "start_date", "end_date"],
    },
    "student_service": {
        "model": "StudentService",
        "fields": ["position", "room", "start_date", "end_date"],
    },
    "finance_service": {
        "model": "FinanceService",
        "fields": ["position", "room", "start_date", "end_date"],
    },
    "general_service": {
        "model": "GeneralService",
        "fields": ["position", "room", "start_date", "end_date"],
    },
    "rector_office": {
        "model": "RectorOffice",
        "fields": ["position", "room", "start_date", "end_date"],
    },
    "quality_insurance": {
        "model": "QualityInsurance",
        "fields": ["position", "room", "start_date", "end_date"],
    },
    "academic_affairs": {
        "model": "AcademicAffairs",
        "fields": ["position", "room", "start_date", "end_date"],
    },
}


# ============== University Admin Service ==============
class UniversityAdminService:
    """Service for university admin dashboard operations - single university focus"""

    @staticmethod
    def get_dashboard_stats(university):
        """Get comprehensive statistics for a single university"""
        return {
            "total_students": Student.objects.all().count(),
            "total_teachers": Teacher.objects.all().count(),
            "total_faculties": Faculty.objects.all().count(),
            "total_departments": Department.objects.all().count(),
            "total_courses": Course.objects.all().count(),
            "active_enrollments": Inscription.objects.filter(
                is_year_close=False,
                regist_status="Active",
            ).count(),
            "completed_exams": Exam.objects.all().count(),
            "pending_requests": Request.objects.all().count(),
        }

    @staticmethod
    def update_university_statistics(university):
        """Update or create statistics for university"""
        stats, _ = UniversityStatistics.objects.get_or_create(university=university)
        stats_data = UniversityAdminService.get_dashboard_stats(university)

        for key, value in stats_data.items():
            setattr(stats, key, value)

        stats.save()
        return stats

    @staticmethod
    def create_notification(
        university,
        recipient,
        title,
        message,
        notification_type="info",
        priority="low",
        action_url=None,
    ):
        """Create notification for admin"""
        return UniversityNotification.objects.create(
            university=university,
            recipient=recipient,
            title=title,
            message=message,
            notification_type=notification_type,
            priority=priority,
            action_url=action_url,
        )


# ============== Configuration Service ==============
class ConfigurationService:
    """Service for university configuration management"""

    @staticmethod
    def get_or_create_config(university, category, key, default_value=None):
        """Get or create a configuration"""
        config, created = UniversityConfiguration.objects.get_or_create(
            university=university,
            category=category,
            key=key,
            defaults={"value": default_value or {}},
        )
        return config

    @staticmethod
    def update_config(university, category, key, value, modified_by):
        """Update configuration value"""
        config = UniversityConfiguration.objects.get(
            university=university, category=category, key=key
        )
        config.value = value
        config.modified_by = modified_by
        config.save()
        return config

    @staticmethod
    def get_category_configs(university, category):
        """Get all configs for a category"""
        return UniversityConfiguration.objects.filter(
            university=university, category=category, is_active=True
        )

    @staticmethod
    def get_all_configs(university):
        """Get all active configurations for university"""
        return UniversityConfiguration.objects.filter(
            university=university, is_active=True
        ).order_by("category", "key")


# ============== University User Management Service ==============
class UniversityUserManagementService:
    """Service for managing users within a university"""

    @staticmethod
    def create_user(
        email, first_name, last_name, password, university=None, role_id=None
    ):
        """Create new user"""
        if User.objects.filter(email=email).exists():
            raise ValueError(f"User with email {email} already exists")

        user = User.objects.create_user(
            email=email,
            first_name=first_name,
            last_name=last_name,
            password=password,
            university=university,
            is_active=True,
        )

        if role_id:
            try:
                role = Role.objects.get(id=role_id)
                user.role = role
                user.save()
            except Role.DoesNotExist:
                pass

        return user

    @staticmethod
    def get_all_users():
        """Get all users"""
        return User.objects.all().select_related("role")

    @staticmethod
    def get_students(academic_year_id=None):
        """Get all student users with optional academic year filter"""
        student_role = Role.objects.filter(name="student").first()
        if not student_role:
            return User.objects.none()

        queryset = User.objects.filter(role=student_role)

        if academic_year_id:
            queryset = queryset.filter(
                student__inscription__academic_year_id=academic_year_id
            ).distinct()

        return queryset

    @staticmethod
    def update_user(user, **kwargs):
        """Update user information"""
        allowed_fields = [
            "first_name",
            "last_name",
            "email",
            "phone_number",
            "is_active",
        ]

        for field, value in kwargs.items():
            if field in allowed_fields and value is not None:
                setattr(user, field, value)

        user.save()
        return user

    @staticmethod
    def change_user_password(user, new_password):
        """Change user password"""
        user.set_password(new_password)
        user.save()
        return user

    @staticmethod
    def assign_role(user, role_id):
        """Assign role to user"""
        try:
            role = Role.objects.get(id=role_id)
            user.role = role
            user.save()
            return user
        except Role.DoesNotExist:
            raise ValueError(f"Role {role_id} not found")

    @staticmethod
    def get_available_roles():
        """Get all available roles"""
        return Role.objects.all()

    @staticmethod
    def deactivate_user(user):
        """Deactivate user"""
        user.is_active = False
        user.save()
        return user

    @staticmethod
    def activate_user(user):
        """Activate user"""
        user.is_active = True
        user.save()
        return user

    @staticmethod
    def create_user_profile(user, position=None, start_date=None):
        """Create profile for user"""
        profile, created = Profile.objects.get_or_create(user=user)

        if position:
            profile.position = position
        if start_date:
            profile.start_date = start_date

        profile.save()
        return profile

    @staticmethod
    def get_user_profile(user):
        """Get user profile"""
        try:
            return Profile.objects.get(user=user)
        except Profile.DoesNotExist:
            return None

    @staticmethod
    def update_user_profile(user, **kwargs):
        """Update user profile"""
        profile = UniversityUserManagementService.get_user_profile(user)
        if not profile:
            profile = UniversityUserManagementService.create_user_profile(user)

        allowed_fields = ["position", "start_date", "end_date"]

        for field, value in kwargs.items():
            if field in allowed_fields and value is not None:
                setattr(profile, field, value)

        profile.save()
        return profile


# ============== Role Profile Service ==============
class RoleProfileService:
    """Service for managing role-specific profiles"""

    @staticmethod
    def get_role_by_name(role_name):
        """Get role by name"""
        try:
            return Role.objects.get(name__iexact=role_name)
        except Role.DoesNotExist:
            return None

    @staticmethod
    def create_user_with_profile(
        university, email, first_name, last_name, password, role_id, profile_data=None
    ):
        """Create user with role-specific profile"""
        if User.objects.filter(email=email).exists():
            raise ValueError(f"User with email {email} already exists")

        # Create user
        user = User.objects.create_user(
            email=email,
            first_name=first_name,
            last_name=last_name,
            password=password,
            university=university,
            is_active=True,
            role_id=role_id,
        )
        role = RoleProfileService.get_role_by_name(role_id)
        role_name = role.name if role else ""
        # Create profile with role-specific data
        if profile_data:
            RoleProfileService.create_profile_for_user(user, role_name, profile_data)

        return user

    @staticmethod
    def create_profile_for_user(user, role_id, profile_data):
        """Create role-specific profile for user"""
        profile, created = Profile.objects.get_or_create(
            user=user, defaults={"start_date": profile_data.get("start_date")}
        )

        role_name_lower = role_id.lower().replace(" ", "_")
        # Set common fields
        if "position" in profile_data:
            profile.position = profile_data["position"]

        if "start_date" in profile_data:
            profile.start_date = profile_data["start_date"]

        if "end_date" in profile_data:
            profile.end_date = profile_data["end_date"]

        # Set room if provided
        if "room_id" in profile_data:
            try:
                room = Room.objects.get(id=profile_data["room_id"])
                profile.room = room
            except Room.DoesNotExist:
                pass

        # Set role-specific fields
        if role_name_lower == "rector" and "university_id" in profile_data:
            try:
                university = University.objects.get(id=profile_data["university_id"])
                profile.university = university
            except University.DoesNotExist:
                pass

        elif role_name_lower == "dean" and "faculty_id" in profile_data:
            try:
                faculty = Faculty.objects.get(id=profile_data["faculty_id"])
                profile.faculty = faculty
            except Faculty.DoesNotExist:
                pass

        profile.save()
        return profile

    @staticmethod
    def update_user_profile(user, role_name, profile_data):
        """Update user profile with role-specific data"""
        try:
            profile = Profile.objects.get(user=user)
        except Profile.DoesNotExist:
            profile = Profile.objects.create(
                user=user, start_date=profile_data.get("start_date")
            )

        role_name_lower = role_name.lower().replace(" ", "_")

        # Update common fields
        if "position" in profile_data:
            profile.position = profile_data["position"]

        if "start_date" in profile_data:
            profile.start_date = profile_data["start_date"]

        if "end_date" in profile_data:
            profile.end_date = profile_data["end_date"]

        if "room_id" in profile_data:
            try:
                room = Room.objects.get(id=profile_data["room_id"])
                profile.room = room
            except Room.DoesNotExist:
                pass

        # Update role-specific fields
        if role_name_lower == "rector" and "university_id" in profile_data:
            try:
                university = University.objects.get(id=profile_data["university_id"])
                profile.university = university
            except University.DoesNotExist:
                pass

        elif role_name_lower == "dean" and "faculty_id" in profile_data:
            try:
                faculty = Faculty.objects.get(id=profile_data["faculty_id"])
                profile.faculty = faculty
            except Faculty.DoesNotExist:
                pass

        profile.save()
        return profile

    @staticmethod
    def get_profile_fields_for_role(role_name):
        """Get required and optional fields for a role"""
        role_name_lower = role_name.lower().replace(" ", "_")

        base_fields = {
            "position": "string",
            "start_date": "date",
            "end_date": "date (optional)",
            "room_id": "uuid (optional)",
        }

        role_specific = {}

        if role_name_lower == "rector":
            role_specific["university_id"] = "uuid (required)"
        elif role_name_lower == "dean":
            role_specific["faculty_id"] = "uuid (required)"

        return {**base_fields, **role_specific}

    @staticmethod
    def get_user_profile_data(user):
        """Get complete profile data for user"""
        try:
            profile = Profile.objects.get(user=user)
            data = {
                "id": str(profile.id),
                "position": profile.position,
                "start_date": profile.start_date,
                "end_date": profile.end_date,
                "room": str(profile.room.id) if profile.room else None,
            }

            # Add role-specific data
            if user.role:
                role_name = user.role.name.lower().replace(" ", "_")

                if role_name == "rector" and profile.university:
                    data["university"] = str(profile.university.id)
                elif role_name == "dean" and profile.faculty:
                    data["faculty"] = str(profile.faculty.id)

            return data
        except Profile.DoesNotExist:
            return None

    @staticmethod
    def get_all_roles_with_fields():
        """Get all roles with their required fields"""
        roles = Role.objects.all()
        result = []

        for role in roles:
            result.append(
                {
                    "id": str(role.id),
                    "name": role.name,
                    "description": role.description,
                    "fields": RoleProfileService.get_profile_fields_for_role(role.name),
                }
            )

        return result


# ============== Secure Backup Service ==============
class SecureBackupService:
    """Secure backup and restore service using django-dbbackup"""

    BACKUP_DIR = "backups"
    ENCRYPTION_KEY_ENV = "BACKUP_ENCRYPTION_KEY"

    @staticmethod
    def get_encryption_key():
        """Get or generate encryption key"""
        key = os.getenv(SecureBackupService.ENCRYPTION_KEY_ENV)
        if not key:
            key = Fernet.generate_key().decode()
            os.environ[SecureBackupService.ENCRYPTION_KEY_ENV] = key
        return key.encode() if isinstance(key, str) else key

    @staticmethod
    def encrypt_backup(data, key):
        """Encrypt backup data"""
        cipher = Fernet(key)
        return cipher.encrypt(data.encode()).decode()

    @staticmethod
    def decrypt_backup(encrypted_data, key):
        """Decrypt backup data"""
        cipher = Fernet(key)
        return cipher.decrypt(encrypted_data.encode()).decode()

    @staticmethod
    def create_backup(university, initiated_by):
        """Create encrypted backup for university"""
        backup = BackupRecord.objects.create(
            backup_type="full",
            status="running",
            initiated_by=initiated_by,
            metadata={
                "university_id": str(university.id),
                "university_name": university.university_name,
                "encrypted": True,
            },
        )

        try:
            os.makedirs(SecureBackupService.BACKUP_DIR, exist_ok=True)

            # Create backup using django-dbbackup
            output = StringIO()
            call_command("dbbackup", stdout=output, verbosity=0)

            # Get latest backup file
            backup_files = sorted(
                [
                    f
                    for f in os.listdir(SecureBackupService.BACKUP_DIR)
                    if f.endswith(".dump")
                ],
                key=lambda x: os.path.getctime(
                    os.path.join(SecureBackupService.BACKUP_DIR, x)
                ),
                reverse=True,
            )

            if backup_files:
                backup_file = os.path.join(
                    SecureBackupService.BACKUP_DIR, backup_files[0]
                )

                # Read and encrypt backup
                with open(backup_file, "rb") as f:
                    backup_data = f.read()

                key = SecureBackupService.get_encryption_key()
                encrypted_data = SecureBackupService.encrypt_backup(
                    backup_data.decode("latin-1"), key
                )

                # Save encrypted backup
                encrypted_file = backup_file.replace(".dump", ".enc")
                with open(encrypted_file, "w") as f:
                    f.write(encrypted_data)

                file_size = os.path.getsize(encrypted_file)

                backup.mark_completed(file_path=encrypted_file, file_size=file_size)

                # Log success
                AuditLog.objects.create(
                    user=initiated_by,
                    university=university,
                    action="backup_initiated",
                    severity="info",
                    description=f"Encrypted backup created for {university.university_name}",
                    success=True,
                )

                return backup
            else:
                raise Exception("No backup file generated")

        except Exception as e:
            backup.mark_failed(str(e))
            AuditLog.objects.create(
                user=initiated_by,
                university=university,
                action="backup_initiated",
                severity="error",
                description=f"Backup failed for {university.university_name}",
                error_message=str(e),
                success=False,
            )
            raise

    @staticmethod
    def restore_backup(backup_record, performed_by):
        """Restore from encrypted backup"""
        recovery = EmergencyRecovery.objects.create(
            recovery_type="data_recovery",
            performed_by=performed_by,
            status="in_progress",
            reason=f"Restoring from backup {backup_record.id}",
            details={"backup_id": str(backup_record.id)},
        )

        try:
            if not backup_record.file_path or not os.path.exists(
                backup_record.file_path
            ):
                raise Exception("Backup file not found")

            # Decrypt backup
            with open(backup_record.file_path, "r") as f:
                encrypted_data = f.read()

            key = SecureBackupService.get_encryption_key()
            decrypted_data = SecureBackupService.decrypt_backup(encrypted_data, key)

            # Write decrypted data to temp file
            temp_file = backup_record.file_path.replace(".enc", ".tmp")
            with open(temp_file, "w") as f:
                f.write(decrypted_data)

            # Restore using django-dbbackup
            output = StringIO()
            call_command(
                "dbrestore",
                input_filename=temp_file,
                stdout=output,
                verbosity=0,
                interactive=False,
            )

            # Cleanup
            if os.path.exists(temp_file):
                os.remove(temp_file)

            university_id = backup_record.metadata.get("university_id")
            university = University.objects.get(id=university_id)

            recovery.status = "completed"
            recovery.result = (
                f"Successfully restored data for {university.university_name}"
            )
            recovery.completed_at = timezone.now()
            recovery.save()

            AuditLog.objects.create(
                user=performed_by,
                university=university,
                action="restore_initiated",
                severity="info",
                description=f"Data restored from encrypted backup {backup_record.id}",
                success=True,
            )

            return recovery

        except Exception as e:
            recovery.status = "failed"
            recovery.result = str(e)
            recovery.completed_at = timezone.now()
            recovery.save()

            try:
                university_id = backup_record.metadata.get("university_id")
                university = University.objects.get(id=university_id)
                AuditLog.objects.create(
                    user=performed_by,
                    university=university,
                    action="restore_initiated",
                    severity="error",
                    description=f"Restore failed from backup {backup_record.id}",
                    error_message=str(e),
                    success=False,
                )
            except Exception as e:  # Catch all exceptions safely
                print(f"Error setting success: {e}")

            raise

    @staticmethod
    def get_university_backups(university):
        """Get all backups for university"""
        return BackupRecord.objects.filter(
            metadata__university_id=str(university.id)
        ).order_by("-started_at")

    @staticmethod
    def delete_backup(backup_record):
        """Delete backup file securely"""
        if backup_record.file_path and os.path.exists(backup_record.file_path):
            # Overwrite file before deletion for security
            with open(backup_record.file_path, "wb") as f:
                f.write(os.urandom(os.path.getsize(backup_record.file_path)))
            os.remove(backup_record.file_path)

        backup_record.delete()


# ============== Backup Restore Service (Alternative) ==============
class BackupRestoreService:
    """Service for university data backup and restore using super admin models"""

    UNIVERSITY_MODELS = [
        Faculty,
        Department,
        Course,
        Teacher,
        Student,
        Inscription,
        Exam,
        Request,
    ]

    @staticmethod
    def create_backup(university, initiated_by):
        """Create backup record for university data"""
        backup = BackupRecord.objects.create(
            backup_type="full",
            status="running",
            initiated_by=initiated_by,
            metadata={
                "university_id": str(university.id),
                "university_name": university.university_name,
            },
        )

        try:
            # Serialize university data
            backup_data = {}
            for model in BackupRestoreService.UNIVERSITY_MODELS:
                queryset = model.objects.filter(university=university)
                if queryset.exists():
                    backup_data[model.__name__] = json.loads(
                        django_serializers.serialize("json", queryset)
                    )

            # Store backup data in metadata
            backup.metadata["data"] = backup_data
            backup.mark_completed(
                file_path=f"backup_university_{university.id}",
                file_size=len(json.dumps(backup_data)),
            )

            # Log backup action
            AuditLog.objects.create(
                user=initiated_by,
                university=university,
                action="backup_initiated",
                severity="info",
                description=f"Backup created for {university.university_name}",
                success=True,
            )

            return backup
        except Exception as e:
            backup.mark_failed(str(e))
            AuditLog.objects.create(
                user=initiated_by,
                university=university,
                action="backup_initiated",
                severity="error",
                description=f"Backup failed for {university.university_name}",
                error_message=str(e),
                success=False,
            )
            raise

    @staticmethod
    def restore_backup(backup_record, performed_by):
        """Restore university data from backup"""
        recovery = EmergencyRecovery.objects.create(
            recovery_type="data_recovery",
            performed_by=performed_by,
            status="in_progress",
            reason=f"Restoring from backup {backup_record.id}",
            details={"backup_id": str(backup_record.id)},
        )

        try:
            university_id = backup_record.metadata.get("university_id")
            backup_data = backup_record.metadata.get("data", {})

            # Restore data for each model
            for model_name, data in backup_data.items():
                model = next(
                    (
                        m
                        for m in BackupRestoreService.UNIVERSITY_MODELS
                        if m.__name__ == model_name
                    ),
                    None,
                )
                if model and data:
                    django_serializers.deserialize(
                        "json", json.dumps(data), ignorenonexistent=True
                    )

            recovery.status = "completed"
            recovery.result = (
                f"Successfully restored data for university {university_id}"
            )
            recovery.completed_at = timezone.now()
            recovery.save()

            # Log restore action
            university = University.objects.get(id=university_id)
            AuditLog.objects.create(
                user=performed_by,
                university=university,
                action="restore_initiated",
                severity="info",
                description=f"Data restored from backup {backup_record.id}",
                success=True,
            )

            return recovery
        except Exception as e:
            recovery.status = "failed"
            recovery.result = str(e)
            recovery.completed_at = timezone.now()
            recovery.save()

            AuditLog.objects.create(
                user=performed_by,
                university=backup_record.metadata.get("university_id"),
                action="restore_initiated",
                severity="error",
                description=f"Restore failed from backup {backup_record.id}",
                error_message=str(e),
                success=False,
            )
            raise

    @staticmethod
    def get_university_backups(university):
        """Get all backups for a university"""
        return BackupRecord.objects.filter(
            metadata__university_id=str(university.id)
        ).order_by("-started_at")
