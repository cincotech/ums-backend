from rest_framework import status
from rest_framework.response import Response


def success_response(
    data=None, message="Success", status_code=status.HTTP_200_OK, extra=None
):
    """
    Return a standardized success response with optional extra fields.
    """
    response_data = {
        "status": "success",
        "message": message,
        "data": data,
    }

    if extra and isinstance(extra, dict):
        response_data.update(extra)  # merge extra fields like typeError, etc.

    return Response(response_data, status=status_code)


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
            "errors": errors,
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
