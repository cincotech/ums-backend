import logging

from rest_framework import status, viewsets
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response

from core.health_check import HealthCheckService
from core.pagination import StandardResultsSetPagination
from core.response_handler import error_response, success_response, validate_serializer

logger = logging.getLogger("core")


@api_view(["GET"])
@permission_classes([AllowAny])
def health_check(request):
    """
    Health check endpoint for monitoring system status
    Returns overall system health including database and cache status
    """
    health_data = HealthCheckService.perform_health_check()

    http_status = (
        status.HTTP_200_OK
        if health_data["status"] == "healthy"
        else status.HTTP_503_SERVICE_UNAVAILABLE
    )

    return Response(health_data, status=http_status)


@api_view(["GET"])
@permission_classes([AllowAny])
def readiness_check(request):
    """
    Readiness check endpoint - checks if service is ready to accept traffic
    """
    db_status = HealthCheckService.check_database()

    if db_status["status"] == "healthy":
        return Response({"status": "ready"}, status=status.HTTP_200_OK)

    return Response(
        {"status": "not_ready", "reason": db_status["message"]},
        status=status.HTTP_503_SERVICE_UNAVAILABLE,
    )


@api_view(["GET"])
@permission_classes([AllowAny])
def liveness_check(request):
    """
    Liveness check endpoint - checks if service is alive
    """
    return Response({"status": "alive"}, status=status.HTTP_200_OK)


class BaseViewSet(viewsets.ModelViewSet):
    """
    Base ViewSet with standardized response handling
    Pagination is ENABLED by default
    """

    pagination_class = StandardResultsSetPagination
    pagination_enabled = True  # ✅ DEFAULT

    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())

        # 🔥 Disable pagination if explicitly turned off
        if (
            not self.pagination_enabled
            or request.query_params.get("pagination") == "false"
        ):
            serializer = self.get_serializer(queryset, many=True)
            return success_response(
                data=serializer.data,
                message=f"{queryset.model.__name__} list retrieved successfully",
            )

        # ✅ PAGINATED
        page = self.paginate_queryset(queryset)
        serializer = self.get_serializer(page, many=True)

        return success_response(
            data=serializer.data,
            message=f"{queryset.model.__name__} list retrieved successfully",
            extra={
                "pagination": {
                    "count": self.paginator.page.paginator.count,
                    "page_size": self.paginator.page.paginator.per_page,
                    "current_page": self.paginator.page.number,
                    "total_pages": self.paginator.page.paginator.num_pages,
                    "next": self.paginator.get_next_link(),
                    "previous": self.paginator.get_previous_link(),
                }
            },
        )

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        return success_response(
            data=serializer.data,
            message=f"{instance.__class__.__name__} retrieved successfully",
        )

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        validation_error = validate_serializer(serializer)
        if validation_error:
            return validation_error

        self.perform_create(serializer)
        return success_response(
            data=serializer.data,
            message=f"{serializer.instance.__class__.__name__} created successfully",
            status_code=status.HTTP_201_CREATED,
        )

    def update(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data)
        validation_error = validate_serializer(serializer)
        if validation_error:
            return validation_error

        self.perform_update(serializer)
        return success_response(
            data=serializer.data,
            message=f"{instance.__class__.__name__} updated successfully",
        )

    def partial_update(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=True)
        validation_error = validate_serializer(serializer)
        if validation_error:
            return validation_error

        self.perform_update(serializer)
        return success_response(
            data=serializer.data,
            message=f"{instance.__class__.__name__} partially updated successfully",
        )

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        instance.delete()
        return success_response(
            message=f"{instance.__class__.__name__} deleted successfully",
            status_code=status.HTTP_204_NO_CONTENT,
        )

    def handle_exception(self, exc):
        logger.error(str(exc), exc_info=True)
        return error_response(
            message=str(exc),
            status_code=status.HTTP_400_BAD_REQUEST,
        )
