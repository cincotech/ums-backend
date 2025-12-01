from django.contrib.auth import get_user_model
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated

from core.audit import log_security_event, log_user_action
from core.response_handler import error_response, success_response

from .user_management_service import UniversityUserManagementService
from .user_serializers import (
    AssignRoleSerializer,
    ChangePasswordSerializer,
    RoleSerializer,
    UserCreateSerializer,
    UserDetailSerializer,
    UserListSerializer,
    UserProfileSerializer,
    UserUpdateSerializer,
)

User = get_user_model()


def get_admin_university(request):
    """Extract university from admin profile"""
    try:
        return request.user.university
    except AttributeError:
        return None


# ============== User Management ==============
@api_view(["GET", "POST"])
@permission_classes([IsAuthenticated])
def user_list(request):
    """List users or create new user for university"""
    try:
        university = get_admin_university(request)
        if not university:
            return error_response(
                message="University not found",
                status_code=status.HTTP_403_FORBIDDEN,
            )

        if request.method == "GET":
            users = UniversityUserManagementService.get_university_users(university)
            serializer = UserListSerializer(users, many=True)
            log_user_action(
                request, "view", "Listed university users", "User", str(university.id)
            )
            return success_response(
                data=serializer.data, message="Users retrieved successfully"
            )

        elif request.method == "POST":
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


@api_view(["GET", "PUT", "DELETE"])
@permission_classes([IsAuthenticated])
def user_detail(request, user_id):
    """Get, update, or delete user"""
    try:
        university = get_admin_university(request)
        if not university:
            return error_response(
                message="University not found",
                status_code=status.HTTP_403_FORBIDDEN,
            )

        user = User.objects.get(id=user_id, university=university)

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
                request, "delete", f"Deleted user: {user_email}", "User", str(user_id)
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


# ============== Password Management ==============
@api_view(["POST"])
@permission_classes([IsAuthenticated])
def change_user_password(request, user_id):
    """Change user password"""
    try:
        university = get_admin_university(request)
        if not university:
            return error_response(
                message="University not found",
                status_code=status.HTTP_403_FORBIDDEN,
            )

        user = User.objects.get(id=user_id, university=university)
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


# ============== Role Management ==============
@api_view(["GET"])
@permission_classes([IsAuthenticated])
def role_list(request):
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


@api_view(["POST"])
@permission_classes([IsAuthenticated])
def assign_user_role(request, user_id):
    """Assign role to user"""
    try:
        university = get_admin_university(request)
        if not university:
            return error_response(
                message="University not found",
                status_code=status.HTTP_403_FORBIDDEN,
            )

        user = User.objects.get(id=user_id, university=university)
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
                    data=result_serializer.data, message="Role assigned successfully"
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


# ============== User Profile Management ==============
@api_view(["GET", "PUT"])
@permission_classes([IsAuthenticated])
def user_profile(request, user_id):
    """Get or update user profile"""
    try:
        university = get_admin_university(request)
        if not university:
            return error_response(
                message="University not found",
                status_code=status.HTTP_403_FORBIDDEN,
            )

        user = User.objects.get(id=user_id, university=university)

        if request.method == "GET":
            profile = UniversityUserManagementService.get_user_profile(user)
            if not profile:
                return error_response(
                    message="Profile not found", status_code=status.HTTP_404_NOT_FOUND
                )
            serializer = UserProfileSerializer(profile)
            return success_response(
                data=serializer.data, message="Profile retrieved successfully"
            )

        elif request.method == "PUT":
            profile = UniversityUserManagementService.get_user_profile(user)
            if not profile:
                profile = UniversityUserManagementService.create_user_profile(user)

            serializer = UserProfileSerializer(profile, data=request.data, partial=True)
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
                    data=result_serializer.data, message="Profile updated successfully"
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


# ============== User Status Management ==============
@api_view(["POST"])
@permission_classes([IsAuthenticated])
def deactivate_user(request, user_id):
    """Deactivate user"""
    try:
        university = get_admin_university(request)
        if not university:
            return error_response(
                message="University not found",
                status_code=status.HTTP_403_FORBIDDEN,
            )

        user = User.objects.get(id=user_id, university=university)
        UniversityUserManagementService.deactivate_user(user)
        log_user_action(
            request, "update", f"Deactivated user: {user.email}", "User", str(user.id)
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


@api_view(["POST"])
@permission_classes([IsAuthenticated])
def activate_user(request, user_id):
    """Activate user"""
    try:
        university = get_admin_university(request)
        if not university:
            return error_response(
                message="University not found",
                status_code=status.HTTP_403_FORBIDDEN,
            )

        user = User.objects.get(id=user_id, university=university)
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
