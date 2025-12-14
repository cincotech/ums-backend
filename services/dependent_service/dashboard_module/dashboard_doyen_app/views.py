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
from services.dependent_service.dashboard_module.dashboard_academic_secretary_app.models import (
    GradeComplaint,
    JuryDecision,
    JurySession,
    TeacherPaymentClaim,
)
from services.dependent_service.exam_module.exam_app.models import (
    Exam,
    ExamRoom,
    ExamSupervisor,
    ExamType,
)
from services.dependent_service.exam_module.result_app.models import (
    CompiledResult,
    Result,
    Session,
    Supplement,
)
from services.dependent_service.scheduling_module.scheduling_app.models import (
    ActivityReport,
    Attendance,
    ScheduleSlot,
    Timetable,
)

from .models import SecretaryNote, TeacherWorkload, TeachingProgress
from .serializers import (
    ActivityReportSerializer,
    AttendanceSerializer,
    BulkAttendanceSerializer,
    BulkResultEntrySerializer,
    ClassGroupSerializer,
    ClassSerializer,
    ClassStatisticsSerializer,
    CompiledResultSerializer,
    CourseAttributionSerializer,
    DeanDashboardStatsSerializer,
    DepartmentSerializer,
    ExamDetailSerializer,
    ExamRoomSerializer,
    ExamSerializer,
    ExamSupervisorSerializer,
    ExamTypeSerializer,
    GradeComplaintSerializer,
    InscriptionSerializer,
    JuryDecisionSerializer,
    JurySessionSerializer,
    ResultSerializer,
    ScheduleSlotSerializer,
    SecretaryNoteSerializer,
    SessionSerializer,
    StudentGroupAssignmentSerializer,
    StudentSerializer,
    StudentStatisticsSerializer,
    SupplementSerializer,
    TeacherPaymentClaimSerializer,
    TeacherWorkloadDetailSerializer,
    TeacherWorkloadSerializer,
    TeachingProgressDetailSerializer,
    TeachingProgressSerializer,
    TimetableDetailSerializer,
    TimetableOverviewSerializer,
    TimetableSerializer,
)
from .services import (
    ActivityReportService,
    AttendanceManagementService,
    ClassGroupManagementService,
    ClassManagementService,
    DeanDashboardService,
    DepartmentManagementService,
    ExamRoomService,
    ExamService,
    ExamSupervisorService,
    FacultyManagementService,
    GradeComplaintService,
    JuryDecisionService,
    JurySessionService,
    ResultCompilationService,
    ResultEntryService,
    StudentManagementService,
    SupplementService,
    TeacherClaimService,
    TeacherWorkloadService,
    TimetableManagementService,
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
        faculty = request.user.profiles.faculty
        academic_year_id = request.data.get("academic_year_id")

        if not faculty:
            return error_response(message="Faculty  is required")

        result = DeanDashboardService.update_all_teaching_progress(
            faculty.id, academic_year_id
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
        faculty = request.user.profiles.faculty
        academic_year_id = request.data.get("academic_year_id")

        if not faculty:
            return error_response(message="Faculty  is required")

        result = DeanDashboardService.update_all_teacher_workloads(
            faculty.id, academic_year_id
        )

        return success_response(
            data=result,
            message="All teacher workloads updated successfully",
        )

    @action(detail=False, methods=["get"])
    def summary(self, request):
        faculty = request.user.profiles.faculty
        academic_year_id = request.query_params.get("academic_year_id")

        if not faculty:
            return error_response(message="Faculty  is required")

        summary_data = DeanDashboardService.get_teacher_workload_summary(
            faculty.id, academic_year_id
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
        faculty = request.user.profiles.faculty
        academic_year_id = request.query_params.get("academic_year_id")

        if not faculty:
            return error_response(message="Faculty  is required")

        try:
            stats = DeanDashboardService.get_dashboard_statistics(
                faculty.id, academic_year_id
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
        faculty = request.user.profiles.faculty
        academic_year_id = request.query_params.get("academic_year_id")

        if not faculty:
            return error_response(message="Faculty  is required")

        try:
            overview_data = DeanDashboardService.get_timetable_overview(
                faculty.id, academic_year_id
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
        faculty = request.user.profiles.faculty
        academic_year_id = request.query_params.get("academic_year_id")

        if not faculty:
            return error_response(message="Faculty  is required")

        try:
            report_data = DeanDashboardService.get_teaching_progress_report(
                faculty.id, academic_year_id
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
        faculty = request.user.profiles.faculty
        academic_year_id = request.query_params.get("academic_year_id")

        if not faculty:
            return error_response(message="Faculty  is required")

        try:
            stats = DeanDashboardService.get_attribution_statistics(
                faculty.id, academic_year_id
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
        faculty = request.user.profiles.faculty
        academic_year_id = request.query_params.get("academic_year_id")

        if not faculty:
            return error_response(message="Faculty  is required")

        try:
            report_data = DeanDashboardService.get_room_utilization_report(
                faculty.id, academic_year_id
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
        faculty = request.user.profiles.faculty

        if not faculty:
            return error_response(message="Faculty  is required")

        try:
            departments = DepartmentManagementService.get_faculty_departments(
                faculty.id
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
        faculty = request.user.profiles.faculty

        if not faculty:
            return error_response(message="Faculty  is required")

        try:
            classes = ClassManagementService.get_faculty_classes(faculty.id)
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
        faculty = request.user.profiles.faculty
        academic_year_id = request.query_params.get("academic_year_id")

        if not faculty:
            return error_response(message="Faculty  is required")

        try:
            stats = ClassManagementService.get_class_statistics(
                faculty.id, academic_year_id
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

    @action(detail=True, methods=["get"])
    def students(self, request, pk=None):
        try:
            inscriptions = ClassGroupManagementService.get_students_in_group(pk)
            serializer = InscriptionSerializer(inscriptions, many=True)

            return success_response(
                data=serializer.data,
                message="Students in class group retrieved successfully",
            )
        except Exception as e:
            return error_response(
                message="Error retrieving students in class group", errors=str(e)
            )

    @action(detail=True, methods=["post"])
    def assign_student(self, request, pk=None):
        serializer = StudentGroupAssignmentSerializer(data=request.data)
        validation_error = validate_serializer(serializer)
        if validation_error:
            return validation_error

        try:
            student_id = request.data.get("student_id")
            result = ClassGroupManagementService.assign_student_to_group(student_id, pk)

            return success_response(
                data=result,
                message="Student assigned to class group successfully",
            )
        except ValueError as e:
            return error_response(message=str(e))
        except Exception as e:
            return error_response(
                message="Error assigning student to class group", errors=str(e)
            )

    @action(detail=True, methods=["post"])
    def bulk_assign_students(self, request, pk=None):
        student_ids = request.data.get("student_ids", [])

        if not student_ids:
            return error_response(message="Student IDs are required")

        try:
            result = ClassGroupManagementService.bulk_assign_students(pk, student_ids)

            return success_response(
                data=result,
                message=f"{result['assigned_count']} students assigned successfully",
            )
        except ValueError as e:
            return error_response(message=str(e))
        except Exception as e:
            return error_response(
                message="Error assigning students to class group", errors=str(e)
            )

    @action(detail=False, methods=["post"])
    def move_student(self, request):
        student_id = request.data.get("student_id")
        from_group_id = request.data.get("from_group_id")
        to_group_id = request.data.get("to_group_id")

        if not all([student_id, from_group_id, to_group_id]):
            return error_response(
                message="Student ID, from_group_id, and to_group_id are required"
            )

        try:
            result = ClassGroupManagementService.move_student_between_groups(
                student_id, from_group_id, to_group_id
            )

            return success_response(
                data=result,
                message="Student moved between groups successfully",
            )
        except ValueError as e:
            return error_response(message=str(e))
        except Exception as e:
            return error_response(
                message="Error moving student between groups", errors=str(e)
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
        faculty = request.user.profiles.faculty
        academic_year_id = request.query_params.get("academic_year_id")

        if not faculty:
            return error_response(message="Faculty  is required")

        try:
            inscriptions = StudentManagementService.get_faculty_students(
                faculty.id, academic_year_id
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
        faculty = request.user.profiles.faculty
        academic_year_id = request.query_params.get("academic_year_id")

        if not faculty:
            return error_response(message="Faculty  is required")

        try:
            stats = StudentManagementService.get_student_statistics(
                faculty.id, academic_year_id
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
        faculty = request.user.profiles.faculty
        academic_year_id = request.query_params.get("academic_year_id")

        if not faculty:
            return error_response(message="Faculty ID is required")

        try:
            inscriptions = StudentManagementService.get_faculty_students(
                faculty.id, academic_year_id
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
        faculty = request.user.profiles.faculty
        academic_year_id = request.query_params.get("academic_year_id")

        if not faculty:
            return error_response(message="Faculty  is required")

        try:
            overview = FacultyManagementService.get_faculty_overview(
                faculty.id, academic_year_id
            )

            return success_response(
                data=overview,
                message="Faculty overview retrieved successfully",
            )
        except Exception as e:
            return error_response(
                message="Error retrieving faculty overview", errors=str(e)
            )


class ScheduleSlotViewSet(BaseViewSet):
    queryset = ScheduleSlot.objects.all()
    serializer_class = ScheduleSlotSerializer
    permission_classes = [IsDean]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ["day_of_week"]
    search_fields = ["schedule_name"]
    ordering_fields = ["day_of_week", "start_time"]


class TimetableViewSet(BaseViewSet):
    queryset = Timetable.objects.all()
    serializer_class = TimetableSerializer
    permission_classes = [IsDean]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ["class_group", "attribution", "room", "status"]
    search_fields = [
        "class_group__group_name",
        "attribution__course__course_name",
        "room__room_name",
    ]
    ordering_fields = ["start_date", "end_date", "created_date"]

    def get_serializer_class(self):
        if self.action == "retrieve":
            return TimetableDetailSerializer
        return TimetableSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        validation_error = validate_serializer(serializer)
        if validation_error:
            return validation_error

        try:
            timetable = TimetableManagementService.create_timetable(
                class_group_id=request.data.get("class_group"),
                attribution_id=request.data.get("attribution"),
                room_id=request.data.get("room"),
                slot_ids=request.data.get("slots", []),
                start_date=request.data.get("start_date"),
                end_date=request.data.get("end_date"),
                status=request.data.get("status", "Planned"),
                created_by=request.user,
            )

            return success_response(
                data=TimetableSerializer(timetable).data,
                message="Timetable created successfully",
                status_code=status.HTTP_201_CREATED,
            )
        except ValueError as e:
            return error_response(message=str(e))
        except Exception as e:
            return error_response(message="Error creating timetable", errors=str(e))

    def update(self, request, *args, **kwargs):
        timetable_id = kwargs.get("pk")

        try:
            timetable = TimetableManagementService.update_timetable(
                timetable_id=timetable_id,
                class_group_id=request.data.get("class_group"),
                attribution_id=request.data.get("attribution"),
                room_id=request.data.get("room"),
                slot_ids=request.data.get("slots"),
                start_date=request.data.get("start_date"),
                end_date=request.data.get("end_date"),
                status=request.data.get("status"),
            )

            return success_response(
                data=TimetableSerializer(timetable).data,
                message="Timetable updated successfully",
            )
        except ValueError as e:
            return error_response(message=str(e))
        except Exception as e:
            return error_response(message="Error updating timetable", errors=str(e))

    @action(detail=True, methods=["post"])
    def publish(self, request, pk=None):
        try:
            timetable = TimetableManagementService.publish_timetable(pk)
            return success_response(
                data=TimetableSerializer(timetable).data,
                message="Timetable published successfully",
            )
        except Exception as e:
            return error_response(message="Error publishing timetable", errors=str(e))

    @action(detail=False, methods=["get"])
    def by_class_group(self, request):
        class_group_id = request.query_params.get("class_group_id")
        academic_year_id = request.query_params.get("academic_year_id")

        if not class_group_id:
            return error_response(message="Class group ID is required")

        try:
            timetables = TimetableManagementService.get_timetables_by_class_group(
                class_group_id, academic_year_id
            )
            serializer = self.get_serializer(timetables, many=True)

            return success_response(
                data=serializer.data,
                message="Timetables retrieved successfully",
            )
        except Exception as e:
            return error_response(message="Error retrieving timetables", errors=str(e))

    @action(detail=False, methods=["get"])
    def by_class(self, request):
        class_id = request.query_params.get("class_id")
        academic_year_id = request.query_params.get("academic_year_id")

        if not class_id:
            return error_response(message="Class ID is required")

        try:
            timetables = TimetableManagementService.get_timetables_by_class(
                class_id, academic_year_id
            )
            serializer = self.get_serializer(timetables, many=True)

            return success_response(
                data=serializer.data,
                message="Timetables retrieved successfully",
            )
        except Exception as e:
            return error_response(message="Error retrieving timetables", errors=str(e))

    @action(detail=False, methods=["get"])
    def by_day(self, request):
        faculty = request.user.profiles.faculty
        day_of_week = request.query_params.get("day_of_week")
        academic_year_id = request.query_params.get("academic_year_id")

        if not faculty:
            return error_response(message="Faculty is required")

        if not day_of_week:
            return error_response(message="Day of week is required")

        try:
            timetables = TimetableManagementService.get_timetables_by_day(
                day_of_week, faculty.id, academic_year_id
            )
            serializer = self.get_serializer(timetables, many=True)

            return success_response(
                data=serializer.data,
                message="Timetables retrieved successfully",
            )
        except Exception as e:
            return error_response(message="Error retrieving timetables", errors=str(e))


class AttendanceViewSet(BaseViewSet):
    queryset = Attendance.objects.all()
    serializer_class = AttendanceSerializer
    permission_classes = [IsDean]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ["timetable", "student", "status"]
    search_fields = [
        "student__matricule",
        "student__user__first_name",
        "student__user__last_name",
    ]
    ordering_fields = ["status"]

    @action(detail=False, methods=["post"])
    def bulk_create(self, request):
        serializer = BulkAttendanceSerializer(data=request.data)
        validation_error = validate_serializer(serializer)
        if validation_error:
            return validation_error

        try:
            timetable_id = request.data.get("timetable_id")
            attendance_data = request.data.get("attendances", [])

            count = AttendanceManagementService.bulk_create_attendance(
                timetable_id, attendance_data
            )

            return success_response(
                data={"created_count": count},
                message=f"{count} attendance records created successfully",
                status_code=status.HTTP_201_CREATED,
            )
        except ValueError as e:
            return error_response(message=str(e))
        except Exception as e:
            return error_response(
                message="Error creating bulk attendance", errors=str(e)
            )

    @action(detail=False, methods=["get"])
    def by_timetable(self, request):
        timetable_id = request.query_params.get("timetable_id")

        if not timetable_id:
            return error_response(message="Timetable ID is required")

        try:
            attendances = AttendanceManagementService.get_attendance_by_timetable(
                timetable_id
            )
            serializer = self.get_serializer(attendances, many=True)

            return success_response(
                data=serializer.data,
                message="Attendance records retrieved successfully",
            )
        except Exception as e:
            return error_response(
                message="Error retrieving attendance records", errors=str(e)
            )

    @action(detail=False, methods=["get"])
    def by_student(self, request):
        student_id = request.query_params.get("student_id")
        academic_year_id = request.query_params.get("academic_year_id")

        if not student_id:
            return error_response(message="Student ID is required")

        try:
            attendances = AttendanceManagementService.get_attendance_by_student(
                student_id, academic_year_id
            )
            serializer = self.get_serializer(attendances, many=True)

            return success_response(
                data=serializer.data,
                message="Attendance records retrieved successfully",
            )
        except Exception as e:
            return error_response(
                message="Error retrieving attendance records", errors=str(e)
            )

    @action(detail=False, methods=["get"])
    def statistics(self, request):
        class_group_id = request.query_params.get("class_group_id")
        academic_year_id = request.query_params.get("academic_year_id")

        if not class_group_id:
            return error_response(message="Class group ID is required")

        try:
            stats = AttendanceManagementService.get_attendance_statistics(
                class_group_id, academic_year_id
            )

            return success_response(
                data=stats,
                message="Attendance statistics retrieved successfully",
            )
        except Exception as e:
            return error_response(
                message="Error retrieving attendance statistics", errors=str(e)
            )


class ActivityReportViewSet(BaseViewSet):
    queryset = ActivityReport.objects.all()
    serializer_class = ActivityReportSerializer
    permission_classes = [IsDean]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ["timetable"]
    ordering_fields = ["completion_rate", "planned_hours", "delivered_hours"]

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        validation_error = validate_serializer(serializer)
        if validation_error:
            return validation_error

        try:
            report, created = ActivityReportService.create_or_update_report(
                timetable_id=request.data.get("timetable"),
                planned_hours=request.data.get("planned_hours"),
                delivered_hours=request.data.get("delivered_hours"),
                observations=request.data.get("observations"),
            )

            return success_response(
                data=ActivityReportSerializer(report).data,
                message=(
                    "Activity report created successfully"
                    if created
                    else "Activity report updated successfully"
                ),
                status_code=status.HTTP_201_CREATED if created else status.HTTP_200_OK,
            )
        except Exception as e:
            return error_response(
                message="Error creating activity report", errors=str(e)
            )

    @action(detail=False, methods=["get"])
    def by_attribution(self, request):
        attribution_id = request.query_params.get("attribution_id")

        if not attribution_id:
            return error_response(message="Attribution ID is required")

        try:
            reports = ActivityReportService.get_reports_by_attribution(attribution_id)
            serializer = self.get_serializer(reports, many=True)

            return success_response(
                data=serializer.data,
                message="Activity reports retrieved successfully",
            )
        except Exception as e:
            return error_response(
                message="Error retrieving activity reports", errors=str(e)
            )

    @action(detail=False, methods=["get"])
    def by_faculty(self, request):
        faculty = request.user.profiles.faculty
        academic_year_id = request.query_params.get("academic_year_id")

        if not faculty:
            return error_response(message="Faculty is required")

        try:
            reports = ActivityReportService.get_reports_by_faculty(
                faculty.id, academic_year_id
            )
            serializer = self.get_serializer(reports, many=True)

            return success_response(
                data=serializer.data,
                message="Activity reports retrieved successfully",
            )
        except Exception as e:
            return error_response(
                message="Error retrieving activity reports", errors=str(e)
            )


# Exam Management ViewSets
class ExamTypeViewSet(BaseViewSet):
    queryset = ExamType.objects.all()
    serializer_class = ExamTypeSerializer
    permission_classes = [IsDean]
    filter_backends = [SearchFilter, OrderingFilter]
    search_fields = ["exam_type_name"]


class ExamViewSet(BaseViewSet):
    queryset = Exam.objects.all()
    serializer_class = ExamSerializer
    permission_classes = [IsDean]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ["course", "exam_type", "academic_year", "status"]
    search_fields = ["course__course_name", "course__course_code"]
    ordering_fields = ["exam_date", "start_time", "created_at"]

    def get_serializer_class(self):
        if self.action == "retrieve":
            return ExamDetailSerializer
        return ExamSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        validation_error = validate_serializer(serializer)
        if validation_error:
            return validation_error

        try:
            exam = ExamService.create_exam(
                course_id=request.data.get("course"),
                exam_type_id=request.data.get("exam_type"),
                academic_year_id=request.data.get("academic_year"),
                exam_date=request.data.get("exam_date"),
                start_time=request.data.get("start_time"),
                end_time=request.data.get("end_time"),
                created_by=request.user,
            )

            return success_response(
                data=ExamSerializer(exam).data,
                message="Exam created successfully",
                status_code=status.HTTP_201_CREATED,
            )
        except Exception as e:
            return error_response(message="Error creating exam", errors=str(e))

    @action(detail=True, methods=["post"])
    def update_status(self, request, pk=None):
        try:
            new_status = request.data.get("status")
            exam = ExamService.update_exam_status(pk, new_status)

            return success_response(
                data=ExamSerializer(exam).data,
                message="Exam status updated successfully",
            )
        except ValueError as e:
            return error_response(message=str(e))
        except Exception as e:
            return error_response(message="Error updating exam status", errors=str(e))

    @action(detail=True, methods=["post"])
    def assign_rooms(self, request, pk=None):
        try:
            room_assignments = request.data.get("room_assignments", [])
            exam_rooms = ExamRoomService.assign_rooms(pk, room_assignments)

            return success_response(
                data=ExamRoomSerializer(exam_rooms, many=True).data,
                message="Rooms assigned successfully",
            )
        except ValueError as e:
            return error_response(message=str(e))
        except Exception as e:
            return error_response(message="Error assigning rooms", errors=str(e))


class ExamRoomViewSet(BaseViewSet):
    queryset = ExamRoom.objects.all()
    serializer_class = ExamRoomSerializer
    permission_classes = [IsDean]

    @action(detail=True, methods=["post"])
    def assign_supervisors(self, request, pk=None):
        try:
            supervisor_ids = request.data.get("supervisor_ids", [])
            supervisors = ExamSupervisorService.assign_supervisors(pk, supervisor_ids)

            return success_response(
                data=ExamSupervisorSerializer(supervisors, many=True).data,
                message="Supervisors assigned successfully",
            )
        except ValueError as e:
            return error_response(message=str(e))
        except Exception as e:
            return error_response(message="Error assigning supervisors", errors=str(e))


class ExamSupervisorViewSet(BaseViewSet):
    queryset = ExamSupervisor.objects.all()
    serializer_class = ExamSupervisorSerializer
    permission_classes = [IsDean]


# Result Management ViewSets
class SessionViewSet(BaseViewSet):
    queryset = Session.objects.all()
    serializer_class = SessionSerializer
    permission_classes = [IsDean]


class ResultViewSet(BaseViewSet):
    queryset = Result.objects.all()
    serializer_class = ResultSerializer
    permission_classes = [IsDean]
    filter_backends = [DjangoFilterBackend, SearchFilter]
    filterset_fields = ["course", "inscription", "session"]

    def create(self, request, *args, **kwargs):
        try:
            result, created = ResultEntryService.enter_mark(
                course_id=request.data.get("course"),
                inscription_id=request.data.get("inscription"),
                session_id=request.data.get("session"),
                mark=request.data.get("mark"),
            )

            return success_response(
                data=ResultSerializer(result).data,
                message=(
                    "Result created successfully"
                    if created
                    else "Result updated successfully"
                ),
                status_code=status.HTTP_201_CREATED if created else status.HTTP_200_OK,
            )
        except ValueError as e:
            return error_response(message=str(e))
        except Exception as e:
            return error_response(message="Error entering result", errors=str(e))

    @action(detail=False, methods=["post"])
    def bulk_entry(self, request):
        serializer = BulkResultEntrySerializer(data=request.data)
        validation_error = validate_serializer(serializer)
        if validation_error:
            return validation_error

        try:
            marks_data = request.data.get("marks", [])
            results = ResultEntryService.bulk_enter_marks(marks_data)

            return success_response(
                data={"count": len(results)},
                message=f"{len(results)} results entered successfully",
            )
        except ValueError as e:
            return error_response(message=str(e))
        except Exception as e:
            return error_response(message="Error entering bulk results", errors=str(e))


class CompiledResultViewSet(BaseViewSet):
    queryset = CompiledResult.objects.all()
    serializer_class = CompiledResultSerializer
    permission_classes = [IsDean]
    filter_backends = [DjangoFilterBackend, SearchFilter]
    filterset_fields = ["inscription", "status", "is_promoted"]

    @action(detail=False, methods=["post"])
    def compile(self, request):
        try:
            inscription_id = request.data.get("inscription_id")
            compiled_result = ResultCompilationService.compile_results(inscription_id)

            return success_response(
                data=CompiledResultSerializer(compiled_result).data,
                message="Results compiled successfully",
            )
        except ValueError as e:
            return error_response(message=str(e))
        except Exception as e:
            return error_response(message="Error compiling results", errors=str(e))

    @action(detail=False, methods=["get"])
    def promotion_statistics(self, request):
        class_id = request.query_params.get("class_id")
        academic_year_id = request.query_params.get("academic_year_id")

        if not class_id or not academic_year_id:
            return error_response(message="class_id and academic_year_id are required")

        try:
            stats = ResultCompilationService.get_promotion_statistics(
                class_id, academic_year_id
            )

            return success_response(
                data=stats,
                message="Promotion statistics retrieved successfully",
            )
        except Exception as e:
            return error_response(
                message="Error retrieving promotion statistics", errors=str(e)
            )


class SupplementViewSet(BaseViewSet):
    queryset = Supplement.objects.all()
    serializer_class = SupplementSerializer
    permission_classes = [IsDean]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ["inscription", "course", "validation"]

    def create(self, request, *args, **kwargs):
        try:
            supplement, created = SupplementService.create_supplement(
                inscription_id=request.data.get("inscription"),
                course_id=request.data.get("course"),
            )

            return success_response(
                data=SupplementSerializer(supplement).data,
                message=(
                    "Supplement created successfully"
                    if created
                    else "Supplement already exists"
                ),
                status_code=status.HTTP_201_CREATED if created else status.HTTP_200_OK,
            )
        except ValueError as e:
            return error_response(message=str(e))
        except Exception as e:
            return error_response(message="Error creating supplement", errors=str(e))

    @action(detail=True, methods=["post"])
    def validate(self, request, pk=None):
        try:
            mark = request.data.get("mark")
            supplement = SupplementService.validate_supplement(pk, mark)

            return success_response(
                data=SupplementSerializer(supplement).data,
                message="Supplement validated successfully",
            )
        except ValueError as e:
            return error_response(message=str(e))
        except Exception as e:
            return error_response(message="Error validating supplement", errors=str(e))


# Jury Management ViewSets
class JurySessionViewSet(BaseViewSet):
    queryset = JurySession.objects.all()
    serializer_class = JurySessionSerializer
    permission_classes = [IsDean]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ["status"]
    search_fields = ["session_name"]
    ordering_fields = ["session_date", "created_at"]

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        validation_error = validate_serializer(serializer)
        if validation_error:
            return validation_error

        try:
            jury_session = JurySessionService.create_jury_session(
                session_name=request.data.get("session_name"),
                session_date=request.data.get("session_date"),
                jury_member_ids=request.data.get("jury_members", []),
                created_by=request.user,
            )

            return success_response(
                data=JurySessionSerializer(jury_session).data,
                message="Jury session created successfully",
                status_code=status.HTTP_201_CREATED,
            )
        except Exception as e:
            return error_response(message="Error creating jury session", errors=str(e))

    @action(detail=True, methods=["post"])
    def update_status(self, request, pk=None):
        try:
            new_status = request.data.get("status")
            jury_session = JurySessionService.update_jury_status(pk, new_status)

            return success_response(
                data=JurySessionSerializer(jury_session).data,
                message="Jury session status updated successfully",
            )
        except ValueError as e:
            return error_response(message=str(e))
        except Exception as e:
            return error_response(
                message="Error updating jury session status", errors=str(e)
            )


class JuryDecisionViewSet(BaseViewSet):
    queryset = JuryDecision.objects.all()
    serializer_class = JuryDecisionSerializer
    permission_classes = [IsDean]
    filter_backends = [DjangoFilterBackend, SearchFilter]
    filterset_fields = ["jury_session", "student", "decision"]

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        validation_error = validate_serializer(serializer)
        if validation_error:
            return validation_error

        try:
            decision, created = JuryDecisionService.validate_decision(
                jury_session_id=request.data.get("jury_session"),
                student_id=request.data.get("student"),
                decision=request.data.get("decision"),
                notes=request.data.get("notes"),
                validated_by=request.user,
            )

            return success_response(
                data=JuryDecisionSerializer(decision).data,
                message="Jury decision validated successfully",
                status_code=status.HTTP_201_CREATED if created else status.HTTP_200_OK,
            )
        except ValueError as e:
            return error_response(message=str(e))
        except Exception as e:
            return error_response(
                message="Error validating jury decision", errors=str(e)
            )


class GradeComplaintViewSet(BaseViewSet):
    queryset = GradeComplaint.objects.all()
    serializer_class = GradeComplaintSerializer
    permission_classes = [IsDean]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ["status", "student", "course"]
    search_fields = ["student__matricule", "course__course_name"]
    ordering_fields = ["submitted_at", "resolved_at"]

    @action(detail=True, methods=["post"])
    def assign(self, request, pk=None):
        try:
            assigned_to_id = request.data.get("assigned_to")
            complaint = GradeComplaintService.assign_complaint(pk, assigned_to_id)

            return success_response(
                data=GradeComplaintSerializer(complaint).data,
                message="Complaint assigned successfully",
            )
        except ValueError as e:
            return error_response(message=str(e))
        except Exception as e:
            return error_response(message="Error assigning complaint", errors=str(e))

    @action(detail=True, methods=["post"])
    def resolve(self, request, pk=None):
        try:
            new_grade = request.data.get("new_grade")
            resolution_notes = request.data.get("resolution_notes")

            complaint = GradeComplaintService.resolve_complaint(
                pk, new_grade, resolution_notes, request.user
            )

            return success_response(
                data=GradeComplaintSerializer(complaint).data,
                message="Complaint resolved successfully",
            )
        except ValueError as e:
            return error_response(message=str(e))
        except Exception as e:
            return error_response(message="Error resolving complaint", errors=str(e))


# Teacher Payment Claim ViewSets
class TeacherPaymentClaimViewSet(BaseViewSet):
    queryset = TeacherPaymentClaim.objects.all()
    serializer_class = TeacherPaymentClaimSerializer
    permission_classes = [IsDean]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ["status", "teacher", "course"]
    search_fields = [
        "teacher__user__first_name",
        "teacher__user__last_name",
        "course__course_name",
    ]
    ordering_fields = ["submitted_at", "processed_at", "total_amount"]

    @action(detail=True, methods=["post"])
    def verify(self, request, pk=None):
        try:
            claim = TeacherClaimService.verify_claim(pk, request.user.id)

            return success_response(
                data=TeacherPaymentClaimSerializer(claim).data,
                message="Claim verified successfully",
            )
        except ValueError as e:
            return error_response(message=str(e))
        except Exception as e:
            return error_response(message="Error verifying claim", errors=str(e))

    @action(detail=True, methods=["post"])
    def approve(self, request, pk=None):
        try:
            claim = TeacherClaimService.approve_claim(pk, request.user.id)

            return success_response(
                data=TeacherPaymentClaimSerializer(claim).data,
                message="Claim approved successfully",
            )
        except ValueError as e:
            return error_response(message=str(e))
        except Exception as e:
            return error_response(message="Error approving claim", errors=str(e))

    @action(detail=True, methods=["post"])
    def sign(self, request, pk=None):
        try:
            claim = TeacherClaimService.sign_claim(pk)

            return success_response(
                data=TeacherPaymentClaimSerializer(claim).data,
                message="Claim signed successfully",
            )
        except ValueError as e:
            return error_response(message=str(e))
        except Exception as e:
            return error_response(message="Error signing claim", errors=str(e))

    @action(detail=True, methods=["post"])
    def send_to_finance(self, request, pk=None):
        try:
            claim = TeacherClaimService.send_to_finance(pk)

            return success_response(
                data=TeacherPaymentClaimSerializer(claim).data,
                message="Claim sent to finance successfully",
            )
        except ValueError as e:
            return error_response(message=str(e))
        except Exception as e:
            return error_response(
                message="Error sending claim to finance", errors=str(e)
            )

    @action(detail=True, methods=["post"])
    def reject(self, request, pk=None):
        try:
            claim = TeacherClaimService.reject_claim(pk)

            return success_response(
                data=TeacherPaymentClaimSerializer(claim).data,
                message="Claim rejected successfully",
            )
        except ValueError as e:
            return error_response(message=str(e))
        except Exception as e:
            return error_response(message="Error rejecting claim", errors=str(e))
