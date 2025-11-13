import logging

from rest_framework import status, viewsets

# Create your views here.
from rest_framework.views import APIView

from core.response_handler import error_response, success_response, validate_serializer

logger = logging.getLogger("core")


class HelloView(APIView):
    def get(self, request):
        logger.debug("Debug info for developers")
        logger.info("User logged in successfully")
        logger.warning("Low disk space")
        logger.error("Payment process failed")
        logger.critical("Database connection lost!")
        try:
            data = {"message": 10 / 0}
            logger.error("An error occurred", exc_info=True)
            return success_response(data=data)
        except Exception as e:
            return error_response(message="Something went wrong", errors=str(e))


class BaseViewSet(viewsets.ModelViewSet):
    """
    Base ViewSet with standardized response handling and permission.
    """

    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        serializer = self.get_serializer(queryset, many=True)
        return success_response(
            data=serializer.data,
            message=f"{self.queryset.model.__name__} list retrieved successfully",
        )

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        return success_response(
            data=serializer.data,
            message=f"{self.queryset.model.__name__} retrieved successfully",
        )

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        validation_error = validate_serializer(serializer)
        if validation_error:
            return validation_error
        serializer.save()
        return success_response(
            data=serializer.data,
            message=f"{self.queryset.model.__name__} created successfully",
            status_code=status.HTTP_201_CREATED,
        )

    def update(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=False)
        validation_error = validate_serializer(serializer)
        if validation_error:
            return validation_error
        serializer.save()
        return success_response(
            data=serializer.data,
            message=f"{self.queryset.model.__name__} updated successfully",
        )

    def partial_update(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=True)
        validation_error = validate_serializer(serializer)
        if validation_error:
            return validation_error
        serializer.save()
        return success_response(
            data=serializer.data,
            message=f"{self.queryset.model.__name__} partially updated successfully",
        )

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        instance.delete()
        return success_response(
            message=f"{self.queryset.model.__name__} deleted successfully",
            status_code=status.HTTP_204_NO_CONTENT,
        )

    def handle_exception(self, exc):
        return error_response(
            message=str(exc),
            status_code=status.HTTP_400_BAD_REQUEST,
        )
