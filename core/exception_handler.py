import logging

from django.core.exceptions import (
    ObjectDoesNotExist,
    PermissionDenied,
    SuspiciousOperation,
    ValidationError,
)
from django.db import IntegrityError, OperationalError
from rest_framework import exceptions, status
from rest_framework.response import Response
from rest_framework.views import exception_handler as drf_exception_handler

from .response_handler import error_response

logger = logging.getLogger(__name__)


def custom_exception_handler(exc, context):
    """
    A global exception handler for all Django/DRF errors.
    """
    # Standard DRF exceptions (like AuthenticationFailed, NotFound, etc.)
    response = drf_exception_handler(exc, context)
    if response is not None:
        logger.warning(f"Handled DRF exception: {exc}")
        return error_response(
            message=str(exc),
            errors=response.data,
            status_code=response.status_code,
        )

    # --- Custom Django and Python errors ---
    if isinstance(exc, ValidationError):
        return error_response(
            message="Validation error.",
            errors=getattr(exc, "message_dict", str(exc)),
            status_code=status.HTTP_400_BAD_REQUEST,
        )

    if isinstance(exc, ObjectDoesNotExist):
        return error_response(
            message="Object not found.",
            errors=str(exc),
            status_code=status.HTTP_404_NOT_FOUND,
        )

    if isinstance(exc, IntegrityError):
        return error_response(
            message="Database integrity error.",
            errors=str(exc),
            status_code=status.HTTP_409_CONFLICT,
        )

    if isinstance(exc, OperationalError):
        return error_response(
            message="Database connection error.",
            errors="Database operation failed. Try again later.",
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
        )

    if isinstance(exc, PermissionDenied):
        return error_response(
            message="Permission denied.",
            errors=str(exc),
            status_code=status.HTTP_403_FORBIDDEN,
        )

    if isinstance(exc, SuspiciousOperation):
        return error_response(
            message="Suspicious operation detected.",
            errors=str(exc),
            status_code=status.HTTP_400_BAD_REQUEST,
        )

    if isinstance(exc, TypeError):
        return error_response(
            message="Type error.",
            errors=str(exc),
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )

    if isinstance(exc, ValueError):
        return error_response(
            message="Invalid value.",
            errors=str(exc),
            status_code=status.HTTP_400_BAD_REQUEST,
        )

    if isinstance(exc, KeyError):
        return error_response(
            message="Missing key in request data.",
            errors=str(exc),
            status_code=status.HTTP_400_BAD_REQUEST,
        )

    if isinstance(exc, exceptions.NotAuthenticated):
        return error_response(
            message="Authentication required.",
            errors=str(exc),
            status_code=status.HTTP_401_UNAUTHORIZED,
        )

    if isinstance(exc, exceptions.NotFound):
        return error_response(
            message="Resource not found.",
            errors=str(exc),
            status_code=status.HTTP_404_NOT_FOUND,
        )

    if isinstance(exc, exceptions.MethodNotAllowed):
        return error_response(
            message="Method not allowed.",
            errors=str(exc),
            status_code=status.HTTP_405_METHOD_NOT_ALLOWED,
        )

    # --- Catch all unknown exceptions ---
    logger.error(f"Unhandled exception: {exc}", exc_info=True)
    return error_response(
        message="An unexpected error occurred.",
        errors=str(exc),
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
    )


def validate_serializer(serializer):
    if not serializer.is_valid():
        return Response(
            {"errors": serializer.errors}, status=status.HTTP_400_BAD_REQUEST
        )
    return None


def success_response(data=None, message="", status_code=status.HTTP_200_OK):
    response = {"message": message}
    if data is not None:
        response["data"] = data
    return Response(response, status=status_code)
