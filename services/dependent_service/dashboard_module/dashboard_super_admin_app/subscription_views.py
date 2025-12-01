from django.contrib.auth import get_user_model
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated

from core.audit import log_security_event, log_user_action
from core.response_handler import error_response, success_response
from services.core_service.academic_module.university_app.models import University

from .subscription_serializers import (
    CreateSubscriptionSerializer,
    ModuleSerializer,
    RenewSubscriptionSerializer,
    UniversityProfileSerializer,
    UniversitySubscriptionSerializer,
)
from .subscription_service import (
    ModuleService,
    SubscriptionService,
    UniversityProfileService,
)

User = get_user_model()


# ============== University Profile ==============
@api_view(["GET", "PUT"])
@permission_classes([IsAuthenticated])
def university_profile(request, university_id):
    """Get or update university profile"""
    try:
        university = University.objects.get(id=university_id)

        if request.method == "GET":
            profile = UniversityProfileService.get_profile(university)
            if not profile:
                return error_response(
                    message="Profile not found", status_code=status.HTTP_404_NOT_FOUND
                )
            serializer = UniversityProfileSerializer(profile)
            return success_response(
                data=serializer.data, message="Profile retrieved successfully"
            )

        elif request.method == "PUT":
            profile = UniversityProfileService.get_profile(university)
            if not profile:
                profile = UniversityProfileService.create_profile(
                    university, request.data.get("contact_email")
                )

            serializer = UniversityProfileSerializer(
                profile, data=request.data, partial=True
            )
            if serializer.is_valid():
                profile = UniversityProfileService.update_profile(
                    university, **serializer.validated_data
                )
                log_user_action(
                    request,
                    "update",
                    f"Updated profile for {university.university_name}",
                    "UniversityProfile",
                    str(profile.id),
                    serializer.validated_data,
                )
                result_serializer = UniversityProfileSerializer(profile)
                return success_response(
                    data=result_serializer.data, message="Profile updated successfully"
                )
            return error_response(
                message="Validation error",
                errors=serializer.errors,
                status_code=status.HTTP_400_BAD_REQUEST,
            )
    except University.DoesNotExist:
        return error_response(
            message="University not found", status_code=status.HTTP_404_NOT_FOUND
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


# ============== Modules ==============
@api_view(["GET"])
@permission_classes([IsAuthenticated])
def module_list(request):
    """Get all available modules"""
    try:
        modules = ModuleService.get_all_modules()
        serializer = ModuleSerializer(modules, many=True)
        return success_response(
            data=serializer.data, message="Modules retrieved successfully"
        )
    except Exception as e:
        return error_response(
            message=f"Error: {str(e)}",
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )


# ============== Subscriptions ==============
@api_view(["GET", "POST"])
@permission_classes([IsAuthenticated])
def university_subscriptions(request, university_id):
    """Get or create subscriptions for university"""
    try:
        university = University.objects.get(id=university_id)

        if request.method == "GET":
            subscriptions = SubscriptionService.get_university_subscriptions(university)
            serializer = UniversitySubscriptionSerializer(subscriptions, many=True)
            return success_response(
                data=serializer.data, message="Subscriptions retrieved successfully"
            )

        elif request.method == "POST":
            serializer = CreateSubscriptionSerializer(data=request.data)
            if serializer.is_valid():
                try:
                    subscription = SubscriptionService.subscribe_university(
                        university=university,
                        module_id=serializer.validated_data["module_id"],
                        start_date=serializer.validated_data["start_date"],
                        end_date=serializer.validated_data["end_date"],
                        created_by=request.user,
                        is_trial=serializer.validated_data.get("is_trial", False),
                    )
                    log_user_action(
                        request,
                        "create",
                        f"Created subscription for {university.university_name}",
                        "UniversitySubscription",
                        str(subscription.id),
                        {"module_id": str(serializer.validated_data["module_id"])},
                    )
                    result_serializer = UniversitySubscriptionSerializer(subscription)
                    return success_response(
                        data=result_serializer.data,
                        message="Subscription created successfully",
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
    except University.DoesNotExist:
        return error_response(
            message="University not found", status_code=status.HTTP_404_NOT_FOUND
        )
    except Exception as e:
        log_security_event(
            request,
            "create",
            f"Subscription creation failed: {str(e)}",
            severity="error",
            success=False,
        )
        return error_response(
            message=f"Error: {str(e)}",
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )


@api_view(["POST"])
@permission_classes([IsAuthenticated])
def cancel_subscription(request, subscription_id):
    """Cancel subscription"""
    try:
        subscription = SubscriptionService.cancel_subscription(
            subscription_id, request.user
        )
        log_user_action(
            request,
            "update",
            "Cancelled subscription",
            "UniversitySubscription",
            str(subscription_id),
        )
        serializer = UniversitySubscriptionSerializer(subscription)
        return success_response(
            data=serializer.data, message="Subscription cancelled successfully"
        )
    except ValueError as e:
        return error_response(
            message=str(e),
            status_code=status.HTTP_400_BAD_REQUEST,
        )
    except Exception as e:
        log_security_event(
            request,
            "update",
            f"Subscription cancellation failed: {str(e)}",
            severity="error",
            success=False,
        )
        return error_response(
            message=f"Error: {str(e)}",
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )


@api_view(["POST"])
@permission_classes([IsAuthenticated])
def renew_subscription(request, subscription_id):
    """Renew subscription"""
    try:
        serializer = RenewSubscriptionSerializer(data=request.data)
        if serializer.is_valid():
            subscription = SubscriptionService.renew_subscription(
                subscription_id, serializer.validated_data["new_end_date"], request.user
            )
            log_user_action(
                request,
                "update",
                "Renewed subscription",
                "UniversitySubscription",
                str(subscription_id),
                {"new_end_date": str(serializer.validated_data["new_end_date"])},
            )
            result_serializer = UniversitySubscriptionSerializer(subscription)
            return success_response(
                data=result_serializer.data, message="Subscription renewed successfully"
            )
        return error_response(
            message="Validation error",
            errors=serializer.errors,
            status_code=status.HTTP_400_BAD_REQUEST,
        )
    except ValueError as e:
        return error_response(
            message=str(e),
            status_code=status.HTTP_400_BAD_REQUEST,
        )
    except Exception as e:
        log_security_event(
            request,
            "update",
            f"Subscription renewal failed: {str(e)}",
            severity="error",
            success=False,
        )
        return error_response(
            message=f"Error: {str(e)}",
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def expiring_subscriptions(request):
    """Get subscriptions expiring soon"""
    try:
        days = int(request.query_params.get("days", 30))
        subscriptions = SubscriptionService.get_expiring_subscriptions(days)
        serializer = UniversitySubscriptionSerializer(subscriptions, many=True)
        return success_response(
            data=serializer.data,
            message=f"Subscriptions expiring within {days} days retrieved successfully",
        )
    except Exception as e:
        return error_response(
            message=f"Error: {str(e)}",
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )
