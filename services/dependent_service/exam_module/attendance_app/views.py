from django.utils import timezone
from django.db.models import Q
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import OrderingFilter, SearchFilter
from rest_framework import status

from core.permissions import IsSupervisor
from core.response_handler import success_response, validate_serializer
from core.views import BaseViewSet
from services.core_service.student_module.student_profile_app.models import Student
from services.dependent_service.exam_module.exam_app.models import Exam, ExamRoom

from .models import ExamAttendance
from .serializers import ExamAttendanceSerializer


class ExamAttendanceViewSet(BaseViewSet):
    queryset = ExamAttendance.objects.all()
    serializer_class = ExamAttendanceSerializer
    permission_classes = [IsSupervisor]

    def create(self, request, *args, **kwargs):
        student_id = request.data.get("student_id")
        if not student_id:
            return success_response(
                data=None,
                message="student_id is required",
                status_code=status.HTTP_400_BAD_REQUEST,
            )

        try:
            student = Student.objects.get(id=student_id)
        except Student.DoesNotExist:
            return success_response(
                data=None,
                message="Student not found",
                status_code=status.HTTP_404_NOT_FOUND,
            )

        inscription = student.inscriptions.filter(regist_status="ACT").first()
        if not inscription:
            return success_response(
                data=None,
                message="No active inscription found for this student",
                status_code=status.HTTP_400_BAD_REQUEST,
            )

        # Find current exam in progress
        now = timezone.now()
        current_exam = Exam.objects.filter(
            status="in_progress", start_time__lte=now, end_time__gte=now
        ).first()

        if not current_exam:
            return success_response(
                data=None,
                message="No exam currently in progress",
                status_code=status.HTTP_400_BAD_REQUEST,
            )

        # Find exam room for this student
        exam_room = ExamRoom.objects.filter(exam=current_exam).first()

        if not exam_room:
            return success_response(
                data=None,
                message="No exam room found for current exam",
                status_code=status.HTTP_400_BAD_REQUEST,
            )

        data = request.data.copy()
        data["inscription"] = inscription.id
        data["examroom"] = exam_room.id
        data["recorded_by"] = request.user.id

        serializer = self.get_serializer(data=data)
        validation_error = validate_serializer(serializer)
        if validation_error:
            return validation_error

        serializer.save()
        return success_response(
            data=serializer.data,
            message="Attendance recorded successfully",
            status_code=status.HTTP_201_CREATED,
        )
