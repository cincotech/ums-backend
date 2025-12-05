from rest_framework import status

from core.permissions import IsAcademicAffairs
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
    permission_classes = [IsAcademicAffairs]


class ExamViewSet(BaseViewSet):
    queryset = Exam.objects.all()
    serializer_class = ExamSerializer
    permission_classes = [IsAcademicAffairs]

    def create(self, request, *args, **kwargs):
        data = request.data.copy()
        data["created_by"] = request.user.id
        serializer = self.get_serializer(data=data)
        validation_error = validate_serializer(serializer)
        if validation_error:
            return validation_error

        serializer.save()
        return success_response(
            data=serializer.data,
            message="Exam created successfully",
            status_code=status.HTTP_201_CREATED,
        )


class ExamRoomViewSet(BaseViewSet):
    queryset = ExamRoom.objects.all()
    serializer_class = ExamRoomSerializer
    permission_classes = [IsAcademicAffairs]


class ExamSupervisorViewSet(BaseViewSet):
    queryset = ExamSupervisor.objects.all()
    serializer_class = ExamSupervisorSerializer
    permission_classes = [IsAcademicAffairs]

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
