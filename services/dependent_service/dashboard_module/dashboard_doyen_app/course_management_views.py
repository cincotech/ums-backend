from rest_framework.decorators import action
from rest_framework.views import APIView

from core.permissions import IsDean
from core.response_handler import error_response, success_response
from services.core_service.academic_module.course_app.models import Course
from services.dependent_service.dashboard_module.dashboard_doyen_app.course_management_serializers import (
    CourseActivityReportSerializer,
    CourseAttributionStatusSerializer,
    CourseBasicSerializer,
    CourseClassSerializer,
    CourseDetailSerializer,
    CourseEnrollmentSerializer,
    CoursePerformanceSerializer,
    CourseStatisticsSerializer,
    CourseSummarySerializer,
    CourseTeacherSerializer,
)
from services.dependent_service.dashboard_module.dashboard_doyen_app.course_management_service import (
    CourseManagementService,
)
from services.dependent_service.dashboard_module.dashboard_doyen_app.views import (
    BaseViewSet,
)


class CourseViewSet(BaseViewSet):
    queryset = Course.objects.all()
    serializer_class = CourseDetailSerializer
    permission_classes = [IsDean]

    def get_queryset(self):
        faculty = self.request.user.profiles.faculty
        if not faculty:
            return Course.objects.none()

        queryset = Course.objects.filter(
            module__class_fk__department__faculty=faculty
        ).distinct()

        academic_year_id = self.request.query_params.get("academic_year_id")
        if academic_year_id:
            queryset = queryset.filter(
                attribution__academic_year_id=academic_year_id
            ).distinct()

        return queryset.select_related(
            "module", "module__class_fk", "module__class_fk__department"
        )

    @action(detail=False, methods=["get"])
    def by_faculty(self, request):
        """Get all courses for the dean's faculty"""
        faculty = request.user.profiles.faculty
        academic_year_id = request.query_params.get("academic_year_id")

        if not faculty:
            return error_response(message="Faculty is required")

        try:
            courses = CourseManagementService.get_faculty_courses(
                faculty.id, academic_year_id
            )
            serializer = CourseBasicSerializer(courses, many=True)

            return success_response(
                data=serializer.data,
                message="Faculty courses retrieved successfully",
            )
        except Exception as e:
            return error_response(
                message="Error retrieving faculty courses", errors=str(e)
            )

    @action(detail=True, methods=["get"])
    def statistics(self, request, pk=None):
        """Get statistics for a specific course"""
        academic_year_id = request.query_params.get("academic_year_id")

        try:
            stats = CourseManagementService.get_course_statistics(pk, academic_year_id)
            serializer = CourseStatisticsSerializer(stats)

            return success_response(
                data=serializer.data,
                message="Course statistics retrieved successfully",
            )
        except Course.DoesNotExist:
            return error_response(message="Course not found")
        except Exception as e:
            return error_response(
                message="Error retrieving course statistics", errors=str(e)
            )

    @action(detail=True, methods=["get"])
    def enrollment(self, request, pk=None):
        """Get enrollment statistics for a course"""
        academic_year_id = request.query_params.get("academic_year_id")

        try:
            enrollment = CourseManagementService.get_course_enrollment(
                pk, academic_year_id
            )
            serializer = CourseEnrollmentSerializer(enrollment)

            return success_response(
                data=serializer.data,
                message="Course enrollment retrieved successfully",
            )
        except Course.DoesNotExist:
            return error_response(message="Course not found")
        except Exception as e:
            return error_response(
                message="Error retrieving course enrollment", errors=str(e)
            )

    @action(detail=True, methods=["get"])
    def performance(self, request, pk=None):
        """Get performance metrics for a course"""
        academic_year_id = request.query_params.get("academic_year_id")

        try:
            performance = CourseManagementService.get_course_performance(
                pk, academic_year_id
            )
            serializer = CoursePerformanceSerializer(performance)

            return success_response(
                data=serializer.data,
                message="Course performance retrieved successfully",
            )
        except Course.DoesNotExist:
            return error_response(message="Course not found")
        except Exception as e:
            return error_response(
                message="Error retrieving course performance", errors=str(e)
            )

    @action(detail=True, methods=["get"])
    def attributions(self, request, pk=None):
        """Get attribution status for a course"""
        academic_year_id = request.query_params.get("academic_year_id")

        try:
            status = CourseManagementService.get_course_attribution_status(
                pk, academic_year_id
            )
            serializer = CourseAttributionStatusSerializer(status)

            return success_response(
                data=serializer.data,
                message="Course attribution status retrieved successfully",
            )
        except Course.DoesNotExist:
            return error_response(message="Course not found")
        except Exception as e:
            return error_response(
                message="Error retrieving course attributions", errors=str(e)
            )

    @action(detail=True, methods=["get"])
    def activity_reports(self, request, pk=None):
        """Get activity reports for a course"""
        academic_year_id = request.query_params.get("academic_year_id")

        try:
            reports = CourseManagementService.get_course_activity_reports(
                pk, academic_year_id
            )
            serializer = CourseActivityReportSerializer(reports, many=True)

            return success_response(
                data=serializer.data,
                message="Course activity reports retrieved successfully",
            )
        except Course.DoesNotExist:
            return error_response(message="Course not found")
        except Exception as e:
            return error_response(
                message="Error retrieving course activity reports", errors=str(e)
            )

    @action(detail=False, methods=["get"])
    def summary(self, request):
        """Get summary of all courses in faculty"""
        faculty = request.user.profiles.faculty
        academic_year_id = request.query_params.get("academic_year_id")

        if not faculty:
            return error_response(message="Faculty is required")

        try:
            summary = CourseManagementService.get_course_summary(
                faculty.id, academic_year_id
            )
            serializer = CourseSummarySerializer(summary)

            return success_response(
                data=serializer.data,
                message="Course summary retrieved successfully",
            )
        except Exception as e:
            return error_response(
                message="Error retrieving course summary", errors=str(e)
            )

    @action(detail=False, methods=["get"])
    def by_class(self, request):
        """Get all courses for a specific class"""
        class_id = request.query_params.get("class_id")
        academic_year_id = request.query_params.get("academic_year_id")

        if not class_id:
            return error_response(message="Class ID is required")

        try:
            courses = CourseManagementService.get_course_by_class(
                class_id, academic_year_id
            )
            serializer = CourseClassSerializer(courses, many=True)

            return success_response(
                data=serializer.data,
                message="Class courses retrieved successfully",
            )
        except Exception as e:
            return error_response(
                message="Error retrieving class courses", errors=str(e)
            )


class CourseByClassView(APIView):
    permission_classes = [IsDean]

    def get(self, request):
        """Get all courses for a specific class"""
        class_id = request.query_params.get("class_id")
        academic_year_id = request.query_params.get("academic_year_id")

        if not class_id:
            return error_response(message="Class ID is required")

        try:
            courses = CourseManagementService.get_course_by_class(
                class_id, academic_year_id
            )
            serializer = CourseClassSerializer(courses, many=True)

            return success_response(
                data=serializer.data,
                message="Class courses retrieved successfully",
            )
        except Exception as e:
            return error_response(
                message="Error retrieving class courses", errors=str(e)
            )


class CourseByTeacherView(APIView):
    permission_classes = [IsDean]

    def get(self, request):
        """Get all courses taught by a specific teacher"""
        teacher_id = request.query_params.get("teacher_id")
        academic_year_id = request.query_params.get("academic_year_id")

        if not teacher_id:
            return error_response(message="Teacher ID is required")

        try:
            courses = CourseManagementService.get_course_by_teacher(
                teacher_id, academic_year_id
            )
            serializer = CourseTeacherSerializer(courses, many=True)

            return success_response(
                data=serializer.data,
                message="Teacher courses retrieved successfully",
            )
        except Exception as e:
            return error_response(
                message="Error retrieving teacher courses", errors=str(e)
            )
