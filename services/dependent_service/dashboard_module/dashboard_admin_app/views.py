from datetime import timedelta

from django.contrib.auth import get_user_model
from django.utils import timezone
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.filters import OrderingFilter, SearchFilter
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.token_blacklist.models import (
    BlacklistedToken,
    OutstandingToken,
)

from core.audit import log_security_event, log_user_action
from core.response_handler import error_response, success_response
from core.views import BaseViewSet
from services.dependent_service.dashboard_module.dashboard_super_admin_app.models import (
    AuditLog,
)
from services.foundational_service.auth_module.authentication_app.services import (
    UserService,
)

from .filters import (
    AuditLogFilter,
    ConfigurationFilter,
    NotificationFilter,
    StatisticsFilter,
    StudentUserFilter,
    UserFilter,
)
from .mixins import UniversityFilterMixin, UniversityRetrieveUpdateDestroyModelMixin
from .models import UniversityConfiguration, UniversityNotification
from .serializers import (
    AssignRoleSerializer,
    AuditLogSerializer,
    BackupRecordSerializer,
    ChangePasswordSerializer,
    CreateRoleProfileSerializer,
    CreateUserWithProfileSerializer,
    EmergencyRecoverySerializer,
    RoleSerializer,
    RoleWithFieldsSerializer,
    UniversityConfigurationSerializer,
    UniversityNotificationSerializer,
    UniversityStatisticsSerializer,
    UserCreateSerializer,
    UserDetailSerializer,
    UserListSerializer,
    UserProfileSerializer,
)
from .services import (
    RoleProfileService,
    SecureBackupService,
    UniversityAdminService,
    UniversityUserManagementService,
)

User = get_user_model()
user_service = UserService()


# ============== Dashboard Overview API ==============
class DashboardAPIView(viewsets.ViewSet):
    """Professional APIView for dashboard overview"""

    permission_classes = [IsAuthenticated]

    @action(detail=False, methods=["get"])
    def overview(self, request):
        """Get admin dashboard overview with all statistics"""
        try:
            university = getattr(request.user, "university", None)
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
            ).exclude(
                id__in=BlacklistedToken.objects.values_list("token_id", flat=True)
            )

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
                message=f"Error: {str(e)}",
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

    @action(detail=False, methods=["post"], url_path="bulk-delete")
    def bulk_delete(self, request):
        """Delete multiple users by IDs."""
        ids = request.data.get("ids", [])
        if not ids:
            return error_response(
                message="Aucun ID fourni.", status_code=status.HTTP_400_BAD_REQUEST
            )

        try:
            users = User.objects.filter(id__in=ids)
            deleted_count, _ = users.delete()
            log_user_action(
                request,
                "bulk_delete",
                f"Bulk deleted {deleted_count} user(s)",
                "User",
                ",".join(str(i) for i in ids),
            )
            return success_response(
                data={"deleted_count": deleted_count},
                message=f"{deleted_count} utilisateur(s) supprimé(s).",
            )
        except Exception as e:
            log_security_event(
                request,
                "bulk_delete",
                f"Bulk delete failed: {str(e)}",
                severity="error",
                success=False,
            )
            return error_response(
                message=f"Error: {str(e)}",
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )


# ============== Configuration Management ==============
class ConfigurationViewSet(
    UniversityFilterMixin, UniversityRetrieveUpdateDestroyModelMixin, BaseViewSet
):
    """Professional ViewSet for university configurations"""

    queryset = UniversityConfiguration.objects.all()
    serializer_class = UniversityConfigurationSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_class = ConfigurationFilter
    filterset_fields = ["category"]
    search_fields = ["key", "value", "category"]
    ordering_fields = ["category", "key", "created_at"]
    ordering = ["category", "key"]

    def get_queryset(self):
        return super().get_queryset()


# ============== Statistics ==============
class StatisticsViewSet(viewsets.ViewSet):
    """Professional APIView for university statistics"""

    permission_classes = [IsAuthenticated]

    @action(detail=False, methods=["get"])
    def university(self, request):
        """Get detailed statistics for university"""
        try:
            university = getattr(request.user, "university", None)
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
                data=serializer.data,
                message="University statistics retrieved successfully",
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
class NotificationViewSet(BaseViewSet):
    """Professional ViewSet for university notifications"""

    queryset = UniversityNotification.objects.all()
    serializer_class = UniversityNotificationSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_class = NotificationFilter
    filterset_class = StatisticsFilter
    filterset_fields = ["notification_type", "is_read"]
    search_fields = ["title", "message", "notification_type"]
    ordering_fields = ["created_at", "is_read"]
    ordering = ["-created_at"]

    def get_queryset(self):
        return UniversityNotification.objects.filter(recipient=self.request.user)

    @action(detail=True, methods=["post"])
    def mark_read(self, request, pk=None):
        """Mark notification as read"""
        try:
            notification = self.get_object()
            notification.mark_as_read()
            log_user_action(
                request,
                "update",
                "Marked notification as read",
                "UniversityNotification",
                str(pk),
            )
            return success_response(message="Notification marked as read")
        except Exception as e:
            return error_response(
                message=f"Error: {str(e)}",
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )


# ============== Audit Logs ==============
class AuditLogViewSet(BaseViewSet):
    """Professional ViewSet for audit logs"""

    queryset = AuditLog.objects.all()
    serializer_class = AuditLogSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_class = AuditLogFilter
    filterset_fields = ["action", "user"]
    search_fields = [
        "action",
        "description",
        "user__email",
        "user__first_name",
        "user__last_name",
        "ip_address",
    ]
    ordering_fields = ["timestamp", "action"]
    ordering = ["-timestamp"]

    def get_queryset(self):
        days = int(self.request.query_params.get("days", 7))
        return AuditLog.objects.filter(
            timestamp__gte=timezone.now() - timedelta(days=days)
        )


# ============== Backup & Restore ==============
class BackupViewSet(viewsets.ViewSet):
    """Professional ViewSet for backup operations"""

    permission_classes = [IsAuthenticated]

    # @action(detail=False, methods=['get'])
    def list(self, request):
        """List backups for university"""
        try:
            university = getattr(request.user, "university", None)
            if not university:
                return error_response(
                    message="University not found",
                    status_code=status.HTTP_403_FORBIDDEN,
                )

            backups = SecureBackupService.get_university_backups(university)
            serializer = BackupRecordSerializer(backups, many=True)
            return success_response(
                data=serializer.data, message="Backups retrieved successfully"
            )
        except Exception as e:
            return error_response(
                message=f"Error: {str(e)}",
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

    # @action(detail=False, methods=['get'])
    def create(self, request):
        """Create new backup"""
        try:
            university = getattr(request.user, "university", None)
            if not university:
                return error_response(
                    message="University not found",
                    status_code=status.HTTP_403_FORBIDDEN,
                )

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

    @action(detail=True, methods=["post"])
    def restore(self, request, pk=None):
        """Restore from backup"""
        try:
            university = getattr(request.user, "university", None)
            if not university:
                return error_response(
                    message="University not found",
                    status_code=status.HTTP_403_FORBIDDEN,
                )

            from services.dependent_service.dashboard_module.dashboard_super_admin_app.models import (
                BackupRecord,
            )

            backup = BackupRecord.objects.get(
                id=pk, metadata__university_id=str(university.id)
            )

            recovery = SecureBackupService.restore_backup(backup, request.user)
            log_user_action(
                request,
                "update",
                f"Restored data from backup {pk}",
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

    @action(detail=True, methods=["delete"])
    def delete(self, request, pk=None):
        """Delete backup securely"""
        try:
            university = getattr(request.user, "university", None)
            if not university:
                return error_response(
                    message="University not found",
                    status_code=status.HTTP_403_FORBIDDEN,
                )

            from services.dependent_service.dashboard_module.dashboard_super_admin_app.models import (
                BackupRecord,
            )

            backup = BackupRecord.objects.get(
                id=pk, metadata__university_id=str(university.id)
            )

            SecureBackupService.delete_backup(backup)
            log_user_action(
                request,
                "delete",
                f"Deleted backup {pk}",
                "BackupRecord",
                str(pk),
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


# ============== User Management ==============
class UserViewSet(BaseViewSet):
    """Professional ViewSet for user management"""

    queryset = User.objects.all()
    serializer_class = UserListSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_class = UserFilter
    filterset_fields = ["role", "is_active", "university"]
    search_fields = ["email", "first_name", "last_name", "phone_number", "role__name"]
    ordering_fields = ["email", "first_name", "last_name", "created_at"]
    ordering = ["-created_at"]

    def get_queryset(self):
        return UniversityUserManagementService.get_all_users()

    def get_serializer_class(self):
        if self.action == "create":
            return UserCreateSerializer
        elif self.action in ["retrieve", "update", "partial_update"]:
            return UserDetailSerializer
        return UserListSerializer

    def perform_create(self, serializer):
        user = UniversityUserManagementService.create_user(
            email=serializer.validated_data["email"],
            first_name=serializer.validated_data.get("first_name", ""),
            last_name=serializer.validated_data.get("last_name", ""),
            password=serializer.validated_data["password"],
            university=serializer.validated_data.get("university"),
            role_id=serializer.validated_data.get("role_id"),
        )
        log_user_action(
            self.request,
            "create",
            f"Created user: {user.email}",
            "User",
            str(user.id),
            {"email": user.email, "role": str(user.role.id) if user.role else None},
        )
        return user

    @action(detail=True, methods=["post"])
    def change_password(self, request, pk=None):
        """Change user password"""
        try:
            user = self.get_object()
            serializer = ChangePasswordSerializer(data=request.data)

            if serializer.is_valid():
                UniversityUserManagementService.change_user_password(
                    user, serializer.validated_data["new_password"]
                )
                log_user_action(
                    request,
                    "update",
                    f"Changed password for user: {user.email}",
                    "User",
                    str(user.id),
                )
                return success_response(message="Password changed successfully")

            return error_response(
                message="Validation error",
                errors=serializer.errors,
                status_code=status.HTTP_400_BAD_REQUEST,
            )
        except User.DoesNotExist:
            return error_response(
                message="User not found", status_code=status.HTTP_404_NOT_FOUND
            )
        except Exception as e:
            log_security_event(
                request,
                "update",
                f"Password change failed: {str(e)}",
                severity="error",
                success=False,
            )
            return error_response(
                message=f"Error: {str(e)}",
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

    @action(detail=True, methods=["post"])
    def assign_role(self, request, pk=None):
        """Assign role to user"""
        try:
            user = self.get_object()
            serializer = AssignRoleSerializer(data=request.data)

            if serializer.is_valid():
                try:
                    user = UniversityUserManagementService.assign_role(
                        user,
                        serializer.validated_data["role_id"],
                        serializer.validated_data.get("teacher_data"),
                    )
                    log_user_action(
                        request,
                        "update",
                        f"Assigned role to user: {user.email}",
                        "User",
                        str(user.id),
                        {"role_id": str(serializer.validated_data["role_id"])},
                    )
                    result_serializer = UserDetailSerializer(user)
                    return success_response(
                        data=result_serializer.data,
                        message="Role assigned successfully",
                    )
                except ValueError as e:
                    return error_response(
                        message=str(e),
                        status_code=status.HTTP_400_BAD_REQUEST,
                    )

            return error_response(
                message="Validation error",
                errors=serializer.errors,
                status_code=status.HTTP_400_BAD_REQUEST,
            )
        except User.DoesNotExist:
            return error_response(
                message="User not found", status_code=status.HTTP_404_NOT_FOUND
            )
        except Exception as e:
            log_security_event(
                request,
                "update",
                f"Role assignment failed: {str(e)}",
                severity="error",
                success=False,
            )
            return error_response(
                message=f"Error: {str(e)}",
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

    @action(detail=True, methods=["get", "put"])
    def profile(self, request, pk=None):
        """Get or update user profile"""
        try:
            user = self.get_object()

            if request.method == "GET":
                profile = UniversityUserManagementService.get_user_profile(user)
                if not profile:
                    return error_response(
                        message="Profile not found",
                        status_code=status.HTTP_404_NOT_FOUND,
                    )
                serializer = UserProfileSerializer(profile)
                return success_response(
                    data=serializer.data, message="Profile retrieved successfully"
                )

            elif request.method == "PUT":
                profile = UniversityUserManagementService.get_user_profile(user)
                if not profile:
                    profile = UniversityUserManagementService.create_user_profile(user)

                serializer = UserProfileSerializer(
                    profile, data=request.data, partial=True
                )
                if serializer.is_valid():
                    profile = UniversityUserManagementService.update_user_profile(
                        user, **serializer.validated_data
                    )
                    log_user_action(
                        request,
                        "update",
                        f"Updated profile for user: {user.email}",
                        "Profile",
                        str(profile.id),
                        serializer.validated_data,
                    )
                    result_serializer = UserProfileSerializer(profile)
                    return success_response(
                        data=result_serializer.data,
                        message="Profile updated successfully",
                    )
                return error_response(
                    message="Validation error",
                    errors=serializer.errors,
                    status_code=status.HTTP_400_BAD_REQUEST,
                )

        except User.DoesNotExist:
            return error_response(
                message="User not found", status_code=status.HTTP_404_NOT_FOUND
            )
        except Exception as e:
            log_security_event(
                request,
                "update",
                f"Profile operation failed: {str(e)}",
                severity="error",
                success=False,
            )
            return error_response(
                message=f"Error: {str(e)}",
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

    @action(detail=True, methods=["post"])
    def deactivate(self, request, pk=None):
        """Deactivate user"""
        try:
            user = self.get_object()
            UniversityUserManagementService.deactivate_user(user)
            log_user_action(
                request,
                "update",
                f"Deactivated user: {user.email}",
                "User",
                str(user.id),
            )
            return success_response(message="User deactivated successfully")
        except User.DoesNotExist:
            return error_response(
                message="User not found", status_code=status.HTTP_404_NOT_FOUND
            )
        except Exception as e:
            return error_response(
                message=f"Error: {str(e)}",
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

    @action(detail=True, methods=["post"])
    def activate(self, request, pk=None):
        """Activate user"""
        try:
            user = self.get_object()
            UniversityUserManagementService.activate_user(user)
            log_user_action(
                request, "update", f"Activated user: {user.email}", "User", str(user.id)
            )
            return success_response(message="User activated successfully")
        except User.DoesNotExist:
            return error_response(
                message="User not found", status_code=status.HTTP_404_NOT_FOUND
            )
        except Exception as e:
            return error_response(
                message=f"Error: {str(e)}",
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

    @action(detail=True, methods=["post"], url_path="verify-email")
    def verify_email(self, request, pk=None):
        """Mark a user's email as verified (admin action)"""
        try:
            user = self.get_object()
            verified = request.data.get("email_verified", True)
            user.email_verified = bool(verified)
            user.save(update_fields=["email_verified"])
            log_user_action(
                request,
                "update",
                f"{'Verified' if verified else 'Unverified'} email for user: {user.email}",
                "User",
                str(user.id),
            )
            return success_response(
                message=f"Email {'verified' if verified else 'unverified'} successfully",
                data={"email": user.email, "email_verified": user.email_verified},
            )
        except Exception as e:
            return error_response(
                message=f"Error: {str(e)}",
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

    @action(detail=True, methods=["post"], url_path="setup-email-2fa")
    def setup_email_2fa(self, request, pk=None):
        """Enable email-based 2FA for a user (admin action)"""
        try:
            user = self.get_object()
            user_service.setup_email_2fa(user)
            user.requires_2fa = True
            user.requires_2fa_email = True
            user.save(update_fields=["requires_2fa", "requires_2fa_email"])
            log_user_action(
                request,
                "update",
                f"Enabled email 2FA for user: {user.email}",
                "User",
                str(user.id),
            )
            return success_response(
                message="Email 2FA enabled successfully",
                data={"email": user.email, "requires_2fa_email": True},
            )
        except Exception as e:
            return error_response(
                message=f"Error: {str(e)}",
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

    @action(detail=True, methods=["post"], url_path="setup-totp-2fa")
    def setup_totp_2fa(self, request, pk=None):
        """Enable TOTP-based 2FA for a user (admin action)"""
        try:
            user = self.get_object()
            device, qr_data = user_service.setup_totp_2fa(user)
            user.requires_2fa = True
            user.requires_2fa_qr = True
            user.save(update_fields=["requires_2fa", "requires_2fa_qr"])
            log_user_action(
                request,
                "update",
                f"Enabled TOTP 2FA for user: {user.email}",
                "User",
                str(user.id),
            )
            return success_response(
                message="TOTP 2FA enabled successfully",
                data={
                    "email": user.email,
                    "requires_2fa_qr": True,
                    "qr_code": qr_data,
                    "config_url": device.config_url,
                },
            )
        except Exception as e:
            return error_response(
                message=f"Error: {str(e)}",
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

    @action(detail=True, methods=["post"], url_path="setup-static-2fa")
    def setup_static_2fa(self, request, pk=None):
        """Enable static token 2FA for a user (admin action)"""
        try:
            user = self.get_object()
            tokens = user_service.setup_static_2fa(user)
            user.requires_2fa = True
            user.requires_2fa_static = True
            user.save(update_fields=["requires_2fa", "requires_2fa_static"])
            log_user_action(
                request,
                "update",
                f"Enabled static 2FA for user: {user.email}",
                "User",
                str(user.id),
            )
            return success_response(
                message="Static 2FA enabled successfully",
                data={"email": user.email, "backup_codes": tokens},
            )
        except Exception as e:
            return error_response(
                message=f"Error: {str(e)}",
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

    @action(detail=True, methods=["post"], url_path="disable-2fa")
    def disable_2fa(self, request, pk=None):
        """Disable all 2FA methods for a user (admin action)"""
        try:
            from django_otp.plugins.otp_email.models import EmailDevice
            from django_otp.plugins.otp_static.models import StaticDevice
            from django_otp.plugins.otp_totp.models import TOTPDevice

            user = self.get_object()
            EmailDevice.objects.filter(user=user).delete()
            TOTPDevice.objects.filter(user=user).delete()
            StaticDevice.objects.filter(user=user).delete()
            user.requires_2fa = False
            user.requires_2fa_email = False
            user.requires_2fa_qr = False
            user.requires_2fa_static = False
            user.totp_secret_key = None
            user.save(
                update_fields=[
                    "requires_2fa",
                    "requires_2fa_email",
                    "requires_2fa_qr",
                    "requires_2fa_static",
                    "totp_secret_key",
                ]
            )
            log_user_action(
                request,
                "update",
                f"Disabled all 2FA for user: {user.email}",
                "User",
                str(user.id),
            )
            return success_response(
                message="All 2FA disabled successfully",
                data={"email": user.email},
            )
        except Exception as e:
            return error_response(
                message=f"Error: {str(e)}",
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )


# ============== Student User Management ==============
class StudentUserViewSet(BaseViewSet):
    """Professional ViewSet for student user management with academic year filtering"""

    queryset = User.objects.all()
    serializer_class = UserListSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_class = StudentUserFilter
    filterset_fields = ["is_active", "student__inscriptions__academic_year"]
    search_fields = [
        "email",
        "first_name",
        "last_name",
        "phone_number",
        "student__matricule",
    ]
    ordering_fields = ["email", "first_name", "last_name", "student__matricule"]
    ordering = ["student__matricule"]

    def get_queryset(self):
        academic_year_id = self.request.query_params.get("academic_year")
        return UniversityUserManagementService.get_students(
            academic_year_id=academic_year_id
        )


# ============== Roles Management ==============
class RoleViewSet(viewsets.ViewSet):
    """Professional ViewSet for role management"""

    permission_classes = [IsAuthenticated]

    # @action(detail=False, methods=['get'])
    def list(self, request):
        """Get available roles"""
        try:
            roles = UniversityUserManagementService.get_available_roles()
            serializer = RoleSerializer(roles, many=True)
            return success_response(
                data=serializer.data, message="Roles retrieved successfully"
            )
        except Exception as e:
            return error_response(
                message=f"Error: {str(e)}",
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )


# ============== Role Profile Management ==============
class RoleProfileViewSet(viewsets.ViewSet):
    """Professional ViewSet for role profile management"""

    permission_classes = [IsAuthenticated]

    @action(detail=False, methods=["get"])
    def fields_info(self, request):
        """Get all roles with their required fields"""
        try:
            roles_data = RoleProfileService.get_all_roles_with_fields()
            serializer = RoleWithFieldsSerializer(roles_data, many=True)
            return success_response(
                data=serializer.data, message="Role information retrieved successfully"
            )
        except Exception as e:
            return error_response(
                message=f"Error: {str(e)}",
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

    # @action(detail=False, methods=['get'])
    def create_with_profile(self, request):
        """Create user with role-specific profile"""
        try:
            university = getattr(request.user, "university", None)
            if not university:
                return error_response(
                    message="University not found",
                    status_code=status.HTTP_403_FORBIDDEN,
                )

            serializer = CreateUserWithProfileSerializer(data=request.data)
            if serializer.is_valid():
                try:
                    profile_data = {
                        "position": serializer.validated_data["position"],
                        "start_date": serializer.validated_data["start_date"],
                        "end_date": serializer.validated_data.get("end_date"),
                        "room_id": serializer.validated_data.get("room_id"),
                        "university_id": serializer.validated_data.get("university_id"),
                        "faculty_id": serializer.validated_data.get("faculty_id"),
                    }

                    user = RoleProfileService.create_user_with_profile(
                        university=university,
                        email=serializer.validated_data["email"],
                        first_name=serializer.validated_data["first_name"],
                        last_name=serializer.validated_data["last_name"],
                        password=serializer.validated_data["password"],
                        role_id=serializer.validated_data["role_id"],
                        profile_data=profile_data,
                    )

                    log_user_action(
                        request,
                        "create",
                        f"Created user with profile: {user.email} ({serializer.validated_data['role_name']})",
                        "User",
                        str(user.id),
                        {
                            "email": user.email,
                            "role": user.role.name if user.role else None,
                            "position": profile_data["position"],
                        },
                    )

                    profile = RoleProfileService.get_user_profile_data(user)
                    return success_response(
                        data={
                            "user_id": str(user.id),
                            "email": user.email,
                            "first_name": user.first_name,
                            "last_name": user.last_name,
                            "role": user.role.name if user.role else None,
                            "profile": profile,
                        },
                        message="User with profile created successfully",
                        status_code=status.HTTP_201_CREATED,
                    )
                except ValueError as e:
                    return error_response(
                        message=str(e),
                        status_code=status.HTTP_400_BAD_REQUEST,
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
                f"User creation failed: {str(e)}",
                severity="error",
                success=False,
            )
            return error_response(
                message=f"Error: {str(e)}",
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

    @action(detail=True, methods=["get"])
    def profile_detail(self, request, pk=None):
        """Get user profile with role-specific data"""
        try:
            university = getattr(request.user, "university", None)
            if not university:
                return error_response(
                    message="University not found",
                    status_code=status.HTTP_403_FORBIDDEN,
                )

            user = User.objects.get(id=pk, university=university)
            profile_data = RoleProfileService.get_user_profile_data(user)

            if not profile_data:
                return error_response(
                    message="Profile not found", status_code=status.HTTP_404_NOT_FOUND
                )

            return success_response(
                data={
                    "user_id": str(user.id),
                    "email": user.email,
                    "first_name": user.first_name,
                    "last_name": user.last_name,
                    "role": user.role.name if user.role else None,
                    "profile": profile_data,
                },
                message="User profile retrieved successfully",
            )
        except User.DoesNotExist:
            return error_response(
                message="User not found", status_code=status.HTTP_404_NOT_FOUND
            )
        except Exception as e:
            return error_response(
                message=f"Error: {str(e)}",
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

    @action(detail=True, methods=["put"])
    def profile_update(self, request, pk=None):
        """Update user profile with role-specific data"""
        try:
            university = getattr(request.user, "university", None)
            if not university:
                return error_response(
                    message="University not found",
                    status_code=status.HTTP_403_FORBIDDEN,
                )

            user = User.objects.get(id=pk, university=university)
            serializer = CreateRoleProfileSerializer(data=request.data)

            if serializer.is_valid():
                profile_data = {
                    "position": serializer.validated_data["position"],
                    "start_date": serializer.validated_data["start_date"],
                    "end_date": serializer.validated_data.get("end_date"),
                    "room_id": serializer.validated_data.get("room_id"),
                    "university_id": serializer.validated_data.get("university_id"),
                    "faculty_id": serializer.validated_data.get("faculty_id"),
                }

                role_id = user.role.name if user.role else "General"
                profile = RoleProfileService.update_user_profile(
                    user, role_id, profile_data
                )

                log_user_action(
                    request,
                    "update",
                    f"Updated profile for user: {user.email}",
                    "Profile",
                    str(profile.id),
                    profile_data,
                )

                profile_data_response = RoleProfileService.get_user_profile_data(user)
                return success_response(
                    data=profile_data_response,
                    message="User profile updated successfully",
                )

            return error_response(
                message="Validation error",
                errors=serializer.errors,
                status_code=status.HTTP_400_BAD_REQUEST,
            )
        except User.DoesNotExist:
            return error_response(
                message="User not found", status_code=status.HTTP_404_NOT_FOUND
            )
        except Exception as e:
            log_security_event(
                request,
                "update",
                f"Profile update failed: {str(e)}",
                severity="error",
                success=False,
            )
            return error_response(
                message=f"Error: {str(e)}",
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

    @action(detail=True, methods=["delete"])
    def profile_delete(self, request, pk=None):
        """Delete the role-specific profile belonging to a user."""
        try:
            university = getattr(request.user, "university", None)
            if not university:
                return error_response(
                    message="University not found",
                    status_code=status.HTTP_403_FORBIDDEN,
                )

            user = User.objects.get(id=pk, university=university)
            profile = user.profiles.first()
            if not profile:
                return error_response(
                    message="Profile not found",
                    status_code=status.HTTP_404_NOT_FOUND,
                )

            profile_id = str(profile.id)
            profile.delete()
            log_user_action(
                request,
                "delete",
                f"Deleted profile for user: {user.email}",
                "Profile",
                profile_id,
            )
            return success_response(message="Profile deleted successfully")
        except User.DoesNotExist:
            return error_response(
                message="User not found", status_code=status.HTTP_404_NOT_FOUND
            )
        except Exception as e:
            log_security_event(
                request,
                "delete",
                f"Profile delete failed: {str(e)}",
                severity="error",
                success=False,
            )
            return error_response(
                message=f"Error: {str(e)}",
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

    @action(detail=False, methods=["post"], url_path="bulk-delete")
    def bulk_delete(self, request):
        """Delete multiple users by IDs."""
        ids = request.data.get("ids", [])
        if not ids:
            return error_response(
                message="Aucun ID fourni.", status_code=status.HTTP_400_BAD_REQUEST
            )

        try:
            users = User.objects.filter(id__in=ids)
            deleted_count, _ = users.delete()
            log_user_action(
                request,
                "bulk_delete",
                f"Bulk deleted {deleted_count} user(s)",
                "User",
                ",".join(str(i) for i in ids),
            )
            return success_response(
                data={"deleted_count": deleted_count},
                message=f"{deleted_count} utilisateur(s) supprimé(s).",
            )
        except Exception as e:
            log_security_event(
                request,
                "bulk_delete",
                f"Bulk delete failed: {str(e)}",
                severity="error",
                success=False,
            )
            return error_response(
                message=f"Error: {str(e)}",
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )
