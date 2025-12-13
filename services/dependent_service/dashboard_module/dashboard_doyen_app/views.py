from django.contrib.auth import get_user_model
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.filters import OrderingFilter, SearchFilter
from rest_framework.views import APIView

from core.permissions import IsDean
from core.response_handler import error_response, success_response, validate_serializer
from core.views import BaseViewSet
from services.core_service.academic_module.class_app.models import Class, ClassGroup
from services.core_service.academic_module.department_app.models import Department
from services.core_service.academic_module.teacher_app.models import Attribution
from services.core_service.student_module.inscription_app.models import Inscription
from services.core_service.student_module.student_profile_app.models import Student

from .models import SecretaryNote, TeacherWorkload, TeachingProgress
from .serializers import (
    ClassGroupSerializer,
    ClassSerializer,
    ClassStatisticsSerializer,
    CourseAttributionSerializer,
    DeanDashboardStatsSerializer,
    DepartmentSerializer,
    InscriptionSerializer,
    SecretaryNoteSerializer,
    StudentSerializer,
    StudentStatisticsSerializer,
    TeacherWorkloadDetailSerializer,
    TeacherWorkloadSerializer,
    TeachingProgressDetailSerializer,
    TeachingProgressSerializer,
    TimetableOverviewSerializer,
)
from .services import (
    ClassManagementService,
    DeanDashboardService,
    DepartmentManagementService,
    FacultyManagementService,
    StudentManagementService,
    TeacherWorkloadService,
)

User = get_user_model()


class TeachingProgressViewSet(BaseViewSet):
    queryset = TeachingProgress.objects.all()
    serializer_class = TeachingProgressSerializer
    permission_classes = [IsDean]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ["faculty", "attribution", "submitted_by"]
    search_fields = [
        "attribution__course__course_name",
        "attribution__course__course_code",
    ]
    ordering_fields = ["progress_percentage", "last_updated"]

    def get_serializer_class(self):
        if self.action == "retrieve":
            return TeachingProgressDetailSerializer
        return TeachingProgressSerializer

    @action(detail=True, methods=["post"])
    def update_progress(self, request, pk=None):
        progress = self.get_object()
        progress.update_progress_from_timetable()

        return success_response(
            data=TeachingProgressDetailSerializer(progress).data,
            message="Teaching progress updated successfully",
        )

    @action(detail=False, methods=["post"])
    def bulk_update(self, request):
        faculty_id = request.data.get("faculty_id")
        academic_year_id = request.data.get("academic_year_id")

        if not faculty_id:
            return error_response(message="Faculty ID is required")

        result = DeanDashboardService.update_all_teaching_progress(
            faculty_id, academic_year_id
        )

        return success_response(
            data=result,
            message="All teaching progress updated successfully",
        )


class TeacherWorkloadViewSet(BaseViewSet):
    queryset = TeacherWorkload.objects.all()
    serializer_class = TeacherWorkloadSerializer
    permission_classes = [IsDean]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ["faculty", "teacher", "academic_year", "is_permanent"]
    search_fields = ["teacher__first_name", "teacher__last_name", "teacher__email"]
    ordering_fields = ["total_hours", "assigned_hours"]

    def get_serializer_class(self):
        if self.action == "retrieve":
            return TeacherWorkloadDetailSerializer
        return TeacherWorkloadSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        validation_error = validate_serializer(serializer)
        if validation_error:
            return validation_error

        teacher_id = request.data.get("teacher")
        faculty_id = request.data.get("faculty")
        academic_year_id = request.data.get("academic_year")
        total_hours = request.data.get("total_hours")
        is_permanent = request.data.get("is_permanent", True)

        workload, created = TeacherWorkloadService.create_or_update_workload(
            teacher_id, faculty_id, academic_year_id, total_hours, is_permanent
        )

        return success_response(
            data=TeacherWorkloadSerializer(workload).data,
            message=(
                "Teacher workload created successfully"
                if created
                else "Teacher workload updated successfully"
            ),
            status_code=status.HTTP_201_CREATED if created else status.HTTP_200_OK,
        )

    @action(detail=True, methods=["post"])
    def update_workload(self, request, pk=None):
        workload = self.get_object()
        workload.update_from_progress()

        return success_response(
            data=TeacherWorkloadDetailSerializer(workload).data,
            message="Teacher workload updated successfully",
        )

    @action(detail=False, methods=["post"])
    def bulk_update(self, request):
        faculty_id = request.data.get("faculty_id")
        academic_year_id = request.data.get("academic_year_id")

        if not faculty_id:
            return error_response(message="Faculty ID is required")

        result = DeanDashboardService.update_all_teacher_workloads(
            faculty_id, academic_year_id
        )

        return success_response(
            data=result,
            message="All teacher workloads updated successfully",
        )

    @action(detail=False, methods=["get"])
    def summary(self, request):
        faculty_id = request.query_params.get("faculty_id")
        academic_year_id = request.query_params.get("academic_year_id")

        if not faculty_id:
            return error_response(message="Faculty ID is required")

        summary_data = DeanDashboardService.get_teacher_workload_summary(
            faculty_id, academic_year_id
        )

        return success_response(
            data=summary_data,
            message="Teacher workload summary retrieved successfully",
        )


class SecretaryNoteViewSet(BaseViewSet):
    queryset = SecretaryNote.objects.all()
    serializer_class = SecretaryNoteSerializer
    permission_classes = [IsDean]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ["faculty", "is_resolved", "created_by"]
    search_fields = ["subject", "message"]
    ordering_fields = ["created_date", "is_resolved"]

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        validation_error = validate_serializer(serializer)
        if validation_error:
            return validation_error

        serializer.save(created_by=request.user)

        return success_response(
            data=serializer.data,
            message="Secretary note created successfully",
            status_code=status.HTTP_201_CREATED,
        )

    @action(detail=True, methods=["post"])
    def mark_resolved(self, request, pk=None):
        note = self.get_object()
        note.is_resolved = True
        note.save()

        return success_response(
            data=SecretaryNoteSerializer(note).data,
            message="Secretary note marked as resolved",
        )

    @action(detail=True, methods=["post"])
    def mark_unresolved(self, request, pk=None):
        note = self.get_object()
        note.is_resolved = False
        note.save()

        return success_response(
            data=SecretaryNoteSerializer(note).data,
            message="Secretary note marked as unresolved",
        )


class DeanDashboardStatsView(APIView):
    permission_classes = [IsDean]

    def get(self, request):
        faculty_id = request.query_params.get("faculty_id")
        academic_year_id = request.query_params.get("academic_year_id")

        if not faculty_id:
            return error_response(message="Faculty ID is required")

        try:
            stats = DeanDashboardService.get_dashboard_statistics(
                faculty_id, academic_year_id
            )
            serializer = DeanDashboardStatsSerializer(stats)

            return success_response(
                data=serializer.data,
                message="Dashboard statistics retrieved successfully",
            )
        except Exception as e:
            return error_response(
                message="Error retrieving dashboard statistics", errors=str(e)
            )


class TimetableOverviewView(APIView):
    permission_classes = [IsDean]

    def get(self, request):
        faculty_id = request.query_params.get("faculty_id")
        academic_year_id = request.query_params.get("academic_year_id")

        if not faculty_id:
            return error_response(message="Faculty ID is required")

        try:
            overview_data = DeanDashboardService.get_timetable_overview(
                faculty_id, academic_year_id
            )
            serializer = TimetableOverviewSerializer(overview_data, many=True)

            return success_response(
                data=serializer.data,
                message="Timetable overview retrieved successfully",
            )
        except Exception as e:
            return error_response(
                message="Error retrieving timetable overview", errors=str(e)
            )


class TeachingProgressReportView(APIView):
    permission_classes = [IsDean]

    def get(self, request):
        faculty_id = request.query_params.get("faculty_id")
        academic_year_id = request.query_params.get("academic_year_id")

        if not faculty_id:
            return error_response(message="Faculty ID is required")

        try:
            report_data = DeanDashboardService.get_teaching_progress_report(
                faculty_id, academic_year_id
            )

            return success_response(
                data=report_data,
                message="Teaching progress report retrieved successfully",
            )
        except Exception as e:
            return error_response(
                message="Error retrieving teaching progress report", errors=str(e)
            )


class AttributionStatisticsView(APIView):
    permission_classes = [IsDean]

    def get(self, request):
        faculty_id = request.query_params.get("faculty_id")
        academic_year_id = request.query_params.get("academic_year_id")

        if not faculty_id:
            return error_response(message="Faculty ID is required")

        try:
            stats = DeanDashboardService.get_attribution_statistics(
                faculty_id, academic_year_id
            )

            return success_response(
                data=stats,
                message="Attribution statistics retrieved successfully",
            )
        except Exception as e:
            return error_response(
                message="Error retrieving attribution statistics", errors=str(e)
            )


class RoomUtilizationReportView(APIView):
    permission_classes = [IsDean]

    def get(self, request):
        faculty_id = request.query_params.get("faculty_id")
        academic_year_id = request.query_params.get("academic_year_id")

        if not faculty_id:
            return error_response(message="Faculty ID is required")

        try:
            report_data = DeanDashboardService.get_room_utilization_report(
                faculty_id, academic_year_id
            )

            return success_response(
                data=report_data,
                message="Room utilization report retrieved successfully",
            )
        except Exception as e:
            return error_response(
                message="Error retrieving room utilization report", errors=str(e)
            )


class CourseAttributionViewSet(BaseViewSet):
    queryset = Attribution.objects.all()
    serializer_class = CourseAttributionSerializer
    permission_classes = [IsDean]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = [
        "course",
        "principal_teacher",
        "academic_year",
        "status_principal_teacher",
    ]
    search_fields = ["course__course_name", "course__course_code"]
    ordering_fields = ["date_attribution", "status_principal_teacher"]

    @action(detail=False, methods=["get"])
    def by_teacher(self, request):
        teacher_id = request.query_params.get("teacher_id")
        academic_year_id = request.query_params.get("academic_year_id")

        if not teacher_id:
            return error_response(message="Teacher ID is required")

        queryset = self.get_queryset().filter(principal_teacher_id=teacher_id)

        if academic_year_id:
            queryset = queryset.filter(academic_year_id=academic_year_id)

        serializer = self.get_serializer(queryset, many=True)

        return success_response(
            data=serializer.data,
            message="Teacher attributions retrieved successfully",
        )

    @action(detail=False, methods=["get"])
    def by_course(self, request):
        course_id = request.query_params.get("course_id")
        academic_year_id = request.query_params.get("academic_year_id")

        if not course_id:
            return error_response(message="Course ID is required")

        queryset = self.get_queryset().filter(course_id=course_id)

        if academic_year_id:
            queryset = queryset.filter(academic_year_id=academic_year_id)

        serializer = self.get_serializer(queryset, many=True)

        return success_response(
            data=serializer.data,
            message="Course attributions retrieved successfully",
        )


class DepartmentViewSet(BaseViewSet):
    queryset = Department.objects.all()
    serializer_class = DepartmentSerializer
    permission_classes = [IsDean]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ["faculty"]
    search_fields = ["department_name", "abreviation"]
    ordering_fields = ["department_name"]

    @action(detail=False, methods=["get"])
    def by_faculty(self, request):
        faculty_id = request.query_params.get("faculty_id")

        if not faculty_id:
            return error_response(message="Faculty ID is required")

        try:
            departments = DepartmentManagementService.get_faculty_departments(
                faculty_id
            )
            serializer = self.get_serializer(departments, many=True)

            return success_response(
                data=serializer.data,
                message="Faculty departments retrieved successfully",
            )
        except Exception as e:
            return error_response(
                message="Error retrieving faculty departments", errors=str(e)
            )

    @action(detail=True, methods=["get"])
    def overview(self, request, pk=None):
        academic_year_id = request.query_params.get("academic_year_id")

        try:
            overview = DepartmentManagementService.get_department_overview(
                pk, academic_year_id
            )

            return success_response(
                data=overview,
                message="Department overview retrieved successfully",
            )
        except Exception as e:
            return error_response(
                message="Error retrieving department overview", errors=str(e)
            )


class ClassViewSet(BaseViewSet):
    queryset = Class.objects.all()
    serializer_class = ClassSerializer
    permission_classes = [IsDean]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ["department"]
    search_fields = ["class_name"]
    ordering_fields = ["class_name"]

    @action(detail=False, methods=["get"])
    def by_faculty(self, request):
        faculty_id = request.query_params.get("faculty_id")

        if not faculty_id:
            return error_response(message="Faculty ID is required")

        try:
            classes = ClassManagementService.get_faculty_classes(faculty_id)
            serializer = self.get_serializer(classes, many=True)

            return success_response(
                data=serializer.data,
                message="Faculty classes retrieved successfully",
            )
        except Exception as e:
            return error_response(
                message="Error retrieving faculty classes", errors=str(e)
            )

    @action(detail=False, methods=["get"])
    def statistics(self, request):
        faculty_id = request.query_params.get("faculty_id")
        academic_year_id = request.query_params.get("academic_year_id")

        if not faculty_id:
            return error_response(message="Faculty ID is required")

        try:
            stats = ClassManagementService.get_class_statistics(
                faculty_id, academic_year_id
            )
            serializer = ClassStatisticsSerializer(stats)

            return success_response(
                data=serializer.data,
                message="Class statistics retrieved successfully",
            )
        except Exception as e:
            return error_response(
                message="Error retrieving class statistics", errors=str(e)
            )


class ClassGroupViewSet(BaseViewSet):
    queryset = ClassGroup.objects.all()
    serializer_class = ClassGroupSerializer
    permission_classes = [IsDean]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ["class_fk", "academic_year"]
    search_fields = ["group_name", "class_fk__class_name"]
    ordering_fields = ["group_name", "created_date"]

    @action(detail=False, methods=["get"])
    def by_class(self, request):
        class_id = request.query_params.get("class_id")
        academic_year_id = request.query_params.get("academic_year_id")

        if not class_id:
            return error_response(message="Class ID is required")

        try:
            groups = ClassManagementService.get_class_groups(class_id, academic_year_id)
            serializer = self.get_serializer(groups, many=True)

            return success_response(
                data=serializer.data,
                message="Class groups retrieved successfully",
            )
        except Exception as e:
            return error_response(
                message="Error retrieving class groups", errors=str(e)
            )


class StudentViewSet(BaseViewSet):
    queryset = Student.objects.all()
    serializer_class = StudentSerializer
    permission_classes = [IsDean]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    search_fields = ["matricule", "user__first_name", "user__last_name", "user__email"]
    ordering_fields = ["matricule", "user__first_name"]

    @action(detail=False, methods=["get"])
    def by_faculty(self, request):
        faculty_id = request.query_params.get("faculty_id")
        academic_year_id = request.query_params.get("academic_year_id")

        if not faculty_id:
            return error_response(message="Faculty ID is required")

        try:
            inscriptions = StudentManagementService.get_faculty_students(
                faculty_id, academic_year_id
            )
            students = [insc.student for insc in inscriptions]
            serializer = self.get_serializer(students, many=True)

            return success_response(
                data=serializer.data,
                message="Faculty students retrieved successfully",
            )
        except Exception as e:
            return error_response(
                message="Error retrieving faculty students", errors=str(e)
            )

    @action(detail=False, methods=["get"])
    def by_class(self, request):
        class_id = request.query_params.get("class_id")
        academic_year_id = request.query_params.get("academic_year_id")

        if not class_id:
            return error_response(message="Class ID is required")

        try:
            inscriptions = StudentManagementService.get_students_by_class(
                class_id, academic_year_id
            )
            students = [insc.student for insc in inscriptions]
            serializer = self.get_serializer(students, many=True)

            return success_response(
                data=serializer.data,
                message="Class students retrieved successfully",
            )
        except Exception as e:
            return error_response(
                message="Error retrieving class students", errors=str(e)
            )

    @action(detail=False, methods=["get"])
    def statistics(self, request):
        faculty_id = request.query_params.get("faculty_id")
        academic_year_id = request.query_params.get("academic_year_id")

        if not faculty_id:
            return error_response(message="Faculty ID is required")

        try:
            stats = StudentManagementService.get_student_statistics(
                faculty_id, academic_year_id
            )
            serializer = StudentStatisticsSerializer(stats)

            return success_response(
                data=serializer.data,
                message="Student statistics retrieved successfully",
            )
        except Exception as e:
            return error_response(
                message="Error retrieving student statistics", errors=str(e)
            )


class InscriptionViewSet(BaseViewSet):
    queryset = Inscription.objects.all()
    serializer_class = InscriptionSerializer
    permission_classes = [IsDean]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ["student", "academic_year", "class_fk", "regist_status"]
    search_fields = [
        "student__matricule",
        "student__user__first_name",
        "student__user__last_name",
    ]
    ordering_fields = ["date_inscription", "regist_status"]

    @action(detail=False, methods=["get"])
    def by_faculty(self, request):
        faculty_id = request.query_params.get("faculty_id")
        academic_year_id = request.query_params.get("academic_year_id")

        if not faculty_id:
            return error_response(message="Faculty ID is required")

        try:
            inscriptions = StudentManagementService.get_faculty_students(
                faculty_id, academic_year_id
            )
            serializer = self.get_serializer(inscriptions, many=True)

            return success_response(
                data=serializer.data,
                message="Faculty inscriptions retrieved successfully",
            )
        except Exception as e:
            return error_response(
                message="Error retrieving faculty inscriptions", errors=str(e)
            )


class FacultyOverviewView(APIView):
    permission_classes = [IsDean]

    def get(self, request):
        faculty_id = request.query_params.get("faculty_id")
        academic_year_id = request.query_params.get("academic_year_id")

        if not faculty_id:
            return error_response(message="Faculty ID is required")

        try:
            overview = FacultyManagementService.get_faculty_overview(
                faculty_id, academic_year_id
            )

            return success_response(
                data=overview,
                message="Faculty overview retrieved successfully",
            )
        except Exception as e:
            return error_response(
                message="Error retrieving faculty overview", errors=str(e)
            )
