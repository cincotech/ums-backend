from datetime import timedelta

from django.contrib.auth import get_user_model
from django.utils import timezone
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
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
    UserUpdateSerializer,
)
from .services import (
    RoleProfileService,
    SecureBackupService,
    UniversityAdminService,
    UniversityUserManagementService,
)

User = get_user_model()


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
                message=f"Error retrieving dashboard: {str(e)}",
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

    def get_queryset(self):
        """Override to handle category filtering"""
        queryset = super().get_queryset()
        category = self.request.query_params.get("category")
        if category:
            queryset = queryset.filter(category=category)
        return queryset.order_by("category", "key")


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
class NotificationViewSet(viewsets.ViewSet):
    """Professional ViewSet for university notifications"""

    permission_classes = [IsAuthenticated]

    # @action(detail=False, methods=['get'])
    def list(self, request):
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

    @action(detail=True, methods=["post"])
    def mark_read(self, request, pk=None):
        """Mark notification as read"""
        try:
            notification = UniversityNotification.objects.get(
                id=pk, recipient=request.user
            )
            notification.mark_as_read()
            log_user_action(
                request,
                "update",
                "Marked notification as read",
                "UniversityNotification",
                str(pk),
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
class AuditLogViewSet(viewsets.ViewSet):
    """Professional APIView for audit logs"""

    permission_classes = [IsAuthenticated]

    # @action(detail=False, methods=['get'])
    def list(self, request):
        """Get audit logs for university"""
        try:
            university = getattr(request.user, "university", None)
            if not university:
                return error_response(
                    message="University not found",
                    status_code=status.HTTP_403_FORBIDDEN,
                )

            days = int(request.query_params.get("days", 7))
            logs = AuditLog.objects.filter(
                timestamp__gte=timezone.now() - timedelta(days=days)
            ).order_by("-timestamp")[:100]

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
class UserViewSet(viewsets.ViewSet):
    """Professional ViewSet for user management"""

    permission_classes = [IsAuthenticated]

    def get_university(self):
        """Get university from current user"""
        university = getattr(self.request.user, "university", None)
        if not university:
            return error_response(
                message="University not found",
                status_code=status.HTTP_403_FORBIDDEN,
            )
        return university

    # @action(detail=False, methods=['get'])
    def list(self, request):
        """List users for university"""
        try:
            university = self.get_university()
            if isinstance(university, Response):
                return university

            users = UniversityUserManagementService.get_university_users(university)
            serializer = UserListSerializer(
                users, many=True, context={"request": request}
            )
            log_user_action(
                request, "view", "Listed university users", "User", str(university.id)
            )
            return success_response(
                data=serializer.data, message="Users retrieved successfully"
            )
        except Exception as e:
            return error_response(
                message=f"Error: {str(e)}",
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

    # @action(detail=False, methods=['get'])
    def create(self, request):
        """Create new user for university"""
        try:
            university = self.get_university()
            if isinstance(university, Response):
                return university

            serializer = UserCreateSerializer(data=request.data)
            if serializer.is_valid():
                try:
                    user = UniversityUserManagementService.create_user(
                        university=university,
                        email=serializer.validated_data["email"],
                        first_name=serializer.validated_data.get("first_name", ""),
                        last_name=serializer.validated_data.get("last_name", ""),
                        password=serializer.validated_data["password"],
                        role_id=serializer.validated_data.get("role_id"),
                    )

                    log_user_action(
                        request,
                        "create",
                        f"Created user: {user.email}",
                        "User",
                        str(user.id),
                        {
                            "email": user.email,
                            "role": str(user.role.id) if user.role else None,
                        },
                    )

                    result_serializer = UserDetailSerializer(user)
                    return success_response(
                        data=result_serializer.data,
                        message="User created successfully",
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

    @action(detail=True, methods=["get", "put", "delete"])
    def detail(self, request, pk=None):
        """Get, update, or delete user"""
        try:
            university = self.get_university()
            if isinstance(university, Response):
                return university

            user = User.objects.get(id=pk, university=university)

            if request.method == "GET":
                serializer = UserDetailSerializer(user)
                log_user_action(
                    request, "view", f"Viewed user: {user.email}", "User", str(user.id)
                )
                return success_response(
                    data=serializer.data, message="User retrieved successfully"
                )

            elif request.method == "PUT":
                serializer = UserUpdateSerializer(user, data=request.data, partial=True)
                if serializer.is_valid():
                    user = serializer.save()
                    log_user_action(
                        request,
                        "update",
                        f"Updated user: {user.email}",
                        "User",
                        str(user.id),
                        request.data,
                    )
                    result_serializer = UserDetailSerializer(user)
                    return success_response(
                        data=result_serializer.data,
                        message="User updated successfully",
                    )
                return error_response(
                    message="Validation error",
                    errors=serializer.errors,
                    status_code=status.HTTP_400_BAD_REQUEST,
                )

            elif request.method == "DELETE":
                user_email = user.email
                user.delete()
                log_user_action(
                    request, "delete", f"Deleted user: {user_email}", "User", str(pk)
                )
                return success_response(message="User deleted successfully")

        except User.DoesNotExist:
            return error_response(
                message="User not found", status_code=status.HTTP_404_NOT_FOUND
            )
        except Exception as e:
            log_security_event(
                request,
                "update",
                f"User operation failed: {str(e)}",
                severity="error",
                success=False,
            )
            return error_response(
                message=f"Error: {str(e)}",
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

    @action(detail=True, methods=["post"])
    def change_password(self, request, pk=None):
        """Change user password"""
        try:
            university = self.get_university()
            if isinstance(university, Response):
                return university

            user = User.objects.get(id=pk, university=university)
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
            university = self.get_university()
            if isinstance(university, Response):
                return university

            user = User.objects.get(id=pk, university=university)
            serializer = AssignRoleSerializer(data=request.data)

            if serializer.is_valid():
                try:
                    user = UniversityUserManagementService.assign_role(
                        user, serializer.validated_data["role_id"]
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
            university = self.get_university()
            if isinstance(university, Response):
                return university

            user = User.objects.get(id=pk, university=university)

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
            university = self.get_university()
            if isinstance(university, Response):
                return university

            user = User.objects.get(id=pk, university=university)
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
            university = self.get_university()
            if isinstance(university, Response):
                return university

            user = User.objects.get(id=pk, university=university)
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
                    user,role_id, profile_data
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
