from rest_framework import status
from rest_framework.response import Response


def success_response(data=None, message="Success", status_code=status.HTTP_200_OK):
    """
    Return a standardized success response
    """
    return Response(
        {
            "status": "success",
            "message": message,
            "data": data,
        },
        status=status_code,
    )


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
