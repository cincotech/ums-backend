import logging

from django.core.exceptions import (
    ObjectDoesNotExist,
    PermissionDenied,
    SuspiciousOperation,
    ValidationError,
)
from django.db import IntegrityError, OperationalError
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import exception_handler as drf_exception_handler

# 🔐 SimpleJWT Exceptions
from rest_framework_simplejwt.exceptions import (
    AuthenticationFailed,
    InvalidToken,
    TokenError,
)

from .response_handler import error_response

logger = logging.getLogger(__name__)


def custom_exception_handler(exc, context):
    """
    A global exception handler for Django/DRF + JWT errors.
    """

    # Standard DRF exceptions (NotFound, AuthenticationFailed, ParseError, etc.)
    response = drf_exception_handler(exc, context)
    if response is not None:
        logger.warning(f"[DRF] handled exception: {exc}")
        return error_response(
            message=str(exc),
            errors=response.data,
            status_code=response.status_code,
        )

    # 🔐 JWT TOKEN ERRORS -------------------------------------------------------
    if isinstance(exc, InvalidToken):
        return error_response(
            message="Invalid or corrupted token.",
            errors=str(exc),
            status_code=status.HTTP_401_UNAUTHORIZED,
        )

    if isinstance(exc, TokenError):
        return error_response(
            message="Token has expired or is no longer valid.",
            errors=str(exc),
            status_code=status.HTTP_401_UNAUTHORIZED,
        )

    if isinstance(exc, AuthenticationFailed):
        return error_response(
            message="Authentication failed. Token might be expired.",
            errors=str(exc),
            status_code=status.HTTP_401_UNAUTHORIZED,
        )

    if isinstance(exc, ValidationError):
        # Get a clean string message
        if hasattr(exc, "message_dict"):
            # Join all field errors
            message_str = " ".join(
                [
                    f"{field}: {'; '.join(messages)}"
                    for field, messages in exc.message_dict.items()
                ]
            )
        elif hasattr(exc, "messages"):
            # Join list of messages
            message_str = " ".join(exc.messages)
        else:
            message_str = str(exc)

        # Return clean message, not list
        return error_response(
            message=message_str,
            errors=None,  # no need for extra 'errors'
            status_code=status.HTTP_400_BAD_REQUEST,
        )

    if isinstance(exc, ObjectDoesNotExist):
        return error_response(
            message="Requested object not found.",
            errors=str(exc),
            status_code=status.HTTP_404_NOT_FOUND,
        )

    if isinstance(exc, IntegrityError):
        logger.error(f"Database integrity error: {exc}")
        return error_response(
            message="Database integrity error.",
            errors=str(exc),
            status_code=status.HTTP_409_CONFLICT,
        )

    if isinstance(exc, OperationalError):
        return error_response(
            message="Database connection problem.",
            errors="Try again later.",
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
        )

    if isinstance(exc, PermissionDenied):
        return error_response(
            message="Access denied.",
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
            message="Type error occurred.",
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
            message="Missing key in request payload.",
            errors=str(exc),
            status_code=status.HTTP_400_BAD_REQUEST,
        )

    # 🛑 FINAL FALLBACK ---------------------------------------------------------
    logger.error(f"Unhandled exception: {exc}", exc_info=True)
    return error_response(
        message="Internal server error occurred.",
        errors=str(exc),
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
    )


# 🎯 Utilities ----------------------------------------------------------------


def validate_serializer(serializer):
    """Validate serializer and return error response automatically."""
    if not serializer.is_valid():
        return Response(
            {"errors": serializer.errors}, status=status.HTTP_400_BAD_REQUEST
        )
    return None


def success_response(data=None, message="", status_code=status.HTTP_200_OK):
    """Unified success JSON for all responses"""
    response = {"message": message}
    if data is not None:
        response["data"] = data
    return Response(response, status=status_code)
