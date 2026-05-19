import json
import logging
from datetime import date, datetime

from rest_framework import status
from rest_framework.response import Response

logger = logging.getLogger(__name__)


def _safe_json_value(obj):
    """Recursively convert any Python date/datetime value to an ISO-format string so JSON serialization can never fail."""
    if isinstance(obj, datetime):
        return obj.isoformat()
    if isinstance(obj, date):
        return obj.isoformat()
    if isinstance(obj, dict):
        return {k: _safe_json_value(v) for k, v in obj.items()}
    if isinstance(obj, (list, tuple)):
        return [_safe_json_value(v) for v in obj]
    return obj


def success_response(
    data=None, message="Success", status_code=status.HTTP_200_OK, extra=None
):
    """
    Return a standardized success response with optional extra fields.
    All date/datetime values are silently converted to ISO strings before the
    response is handed to DRF, preventing ``TypeError: Object of type date is
    not JSON serializable`` from leaking through.
    """
    # Ensure every value in the outer dict is JSON-safe (covers any back-end
    # call that still passes a raw Python date / datetime object).
    safe_data = {
        "status": "success",
        "message": message,
        "data": _safe_json_value(data),
    }

    if extra and isinstance(extra, dict):
        safe_data.update(
            {k: _safe_json_value(v) for k, v in extra.items()}
        )

    return Response(safe_data, status=status_code)


def error_response(
    message="Error", errors=None, status_code=status.HTTP_400_BAD_REQUEST
):
    """
    Return a standardized error response
    """
    return Response(
        {
            "status": "error",
            "message": message,
            "errors": _safe_json_value(errors),
        },
        status=status_code,
    )


def validate_serializer(serializer):
    """
    Validate a DRF serializer and return a standardized error response if invalid.
    """
    if not serializer.is_valid():
        errors = serializer.errors
        # Flatten or format errors
        message = "; ".join(
            [
                f"{field}: {','.join(val) if isinstance(val, list) else str(val)}"
                for field, val in errors.items()
            ]
        )
        return error_response(
            message=message, errors=errors, status_code=status.HTTP_400_BAD_REQUEST
        )
    return None


def paginated_success_response(
    paginator, queryset, serializer_class, request, message="Success"
):
    page = paginator.paginate_queryset(queryset, request)

    serializer = serializer_class(page, many=True)

    return success_response(
        data=serializer.data,
        message=message,
        extra={
            "pagination": {
                "count": paginator.page.paginator.count,
                "page_size": paginator.page.paginator.per_page,
                "current_page": paginator.page.number,
                "total_pages": paginator.page.paginator.num_pages,
                "next": paginator.get_next_link(),
                "previous": paginator.get_previous_link(),
            }
        },
    )
