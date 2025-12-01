from django.contrib.auth import get_user_model
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated

from core.audit import log_security_event, log_user_action
from core.response_handler import error_response, success_response

from .role_profile_serializers import (
    CreateRoleProfileSerializer,
    CreateUserWithProfileSerializer,
    RoleWithFieldsSerializer,
)
from .role_profile_service import RoleProfileService

User = get_user_model()


def get_admin_university(request):
    """Extract university from admin profile"""
    try:
        return request.user.university
    except AttributeError:
        return None


# ============== Role Information ==============
@api_view(["GET"])
@permission_classes([IsAuthenticated])
def role_fields_info(request):
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


# ============== Create User with Profile ==============
@api_view(["POST"])
@permission_classes([IsAuthenticated])
def create_user_with_profile(request):
    """Create user with role-specific profile"""
    try:
        university = get_admin_university(request)
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
                    role_name=serializer.validated_data["role_name"],
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
                        "role": serializer.validated_data["role_name"],
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


# ============== Update User Profile ==============
@api_view(["PUT"])
@permission_classes([IsAuthenticated])
def update_user_profile(request, user_id):
    """Update user profile with role-specific data"""
    try:
        university = get_admin_university(request)
        if not university:
            return error_response(
                message="University not found",
                status_code=status.HTTP_403_FORBIDDEN,
            )

        user = User.objects.get(id=user_id, university=university)
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

            role_name = user.role.name if user.role else "General"
            profile = RoleProfileService.update_user_profile(
                user, role_name, profile_data
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
                data=profile_data_response, message="User profile updated successfully"
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


# ============== Get User Profile ==============
@api_view(["GET"])
@permission_classes([IsAuthenticated])
def get_user_profile(request, user_id):
    """Get user profile with role-specific data"""
    try:
        university = get_admin_university(request)
        if not university:
            return error_response(
                message="University not found",
                status_code=status.HTTP_403_FORBIDDEN,
            )

        user = User.objects.get(id=user_id, university=university)
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
