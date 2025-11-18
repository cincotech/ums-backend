from rest_framework import status
from rest_framework.permissions import IsAuthenticated

from core.response_handler import success_response, validate_serializer
from core.views import BaseViewSet

from .models import Exam, ExamRoom, ExamSupervisor, ExamType
from .serializers import (
    ExamRoomSerializer,
    ExamSerializer,
    ExamSupervisorSerializer,
    ExamTypeSerializer,
)


class ExamTypeViewSet(BaseViewSet):
    queryset = ExamType.objects.all()
    serializer_class = ExamTypeSerializer
    permission_classes = [IsAuthenticated]


class ExamViewSet(BaseViewSet):
    queryset = Exam.objects.all()
    serializer_class = ExamSerializer
    permission_classes = [IsAuthenticated]

    def create(self, request, *args, **kwargs):
        request.data._mutable = True
        request.data["status"] = "scheduled"
        return super().create(request, *args, **kwargs)


class ExamRoomViewSet(BaseViewSet):
    queryset = ExamRoom.objects.all()
    serializer_class = ExamRoomSerializer
    permission_classes = [IsAuthenticated]


class ExamSupervisorViewSet(BaseViewSet):
    queryset = ExamSupervisor.objects.all()
    serializer_class = ExamSupervisorSerializer
    permission_classes = [IsAuthenticated]

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        validation_error = validate_serializer(serializer)
        if validation_error:
            return validation_error

        serializer.save()
        return success_response(
            data=serializer.data,
            message="Supervisor assigned successfully",
            status_code=status.HTTP_201_CREATED,
        )
