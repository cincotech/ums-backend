from django.db.models import Q
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import OrderingFilter, SearchFilter
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated

from core.permissions import IsTeacher
from core.response_handler import error_response, success_response

from .serializers import (
    AttendanceEntrySerializer,
    AttendanceRecordSerializer,
    AttributionSerializer,
    BulkGradeEntrySerializer,
    GradeEntrySerializer,
    ResultSerializer,
    TeacherCourseSerializer,
    TeacherCourseStudentSerializer,
    TeacherDashboardStatsSerializer,
    TeacherExamSerializer,
    TeacherMessageSerializer,
    TeacherNotificationSerializer,
    TeacherPaymentClaimSerializer,
    TeacherProfileSerializer,
    TeacherScheduleSerializer,
    TeachingStatisticsSerializer,
)
from .services import TeacherDashboardService


@api_view(["GET"])
@permission_classes([IsAuthenticated, IsTeacher])
def teacher_dashboard_overview(request):
    """Get teacher dashboard overview"""
    try:
        teacher = request.user.teachers
        stats = TeacherDashboardService.get_teacher_dashboard_stats(teacher)
        serializer = TeacherDashboardStatsSerializer(stats)
        return success_response(
            data=serializer.data, message="Teacher dashboard overview retrieved"
        )
    except Exception as e:
        return error_response(
            message=f"Error: {str(e)}",
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )


@api_view(["GET"])
@permission_classes([IsAuthenticated, IsTeacher])
def teacher_profile(request):
    """Get teacher profile"""
    try:
        teacher = request.user.teachers
        profile_data = TeacherDashboardService.get_teacher_profile(teacher)
        serializer = TeacherProfileSerializer(profile_data)
        return success_response(
            data=serializer.data, message="Teacher profile retrieved"
        )
    except Exception as e:
        return error_response(
            message=f"Error: {str(e)}",
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )


@api_view(["GET"])
@permission_classes([IsAuthenticated, IsTeacher])
def teacher_attributions(request):
    """Get teacher course attributions"""
    try:
        teacher = request.user.teachers
        attributions = TeacherDashboardService.get_teacher_attributions(teacher)
        serializer = AttributionSerializer(attributions, many=True)
        return success_response(data=serializer.data, message="Attributions retrieved")
    except Exception as e:
        return error_response(
            message=f"Error: {str(e)}",
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )


@api_view(["POST"])
@permission_classes([IsAuthenticated, IsTeacher])
def accept_attribution(request, attribution_id):
    """Accept a course attribution"""
    try:
        teacher = request.user.teachers
        attribution = TeacherDashboardService.accept_attribution(
            attribution_id, teacher
        )
        serializer = AttributionSerializer(attribution)
        return success_response(data=serializer.data, message="Attribution accepted")
    except ValueError as e:
        return error_response(message=str(e), status_code=status.HTTP_400_BAD_REQUEST)
    except Exception as e:
        return error_response(
            message=f"Error: {str(e)}",
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )


@api_view(["POST"])
@permission_classes([IsAuthenticated, IsTeacher])
def refuse_attribution(request, attribution_id):
    """Refuse a course attribution"""
    try:
        teacher = request.user.teachers
        comment = request.data.get("comment", "")
        attribution = TeacherDashboardService.refuse_attribution(
            attribution_id, teacher, comment
        )
        serializer = AttributionSerializer(attribution)
        return success_response(data=serializer.data, message="Attribution refused")
    except ValueError as e:
        return error_response(message=str(e), status_code=status.HTTP_400_BAD_REQUEST)
    except Exception as e:
        return error_response(
            message=f"Error: {str(e)}",
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )


@api_view(["GET"])
@permission_classes([IsAuthenticated, IsTeacher])
def teacher_courses(request):
    """Get courses currently taught by teacher"""
    try:
        teacher = request.user.teachers
        courses = TeacherDashboardService.get_teacher_courses(teacher)
        serializer = TeacherCourseSerializer(courses, many=True)
        return success_response(data=serializer.data, message="Courses retrieved")
    except Exception as e:
        return error_response(
            message=f"Error: {str(e)}",
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )


@api_view(["GET"])
@permission_classes([IsAuthenticated, IsTeacher])
def course_students(request, course_id):
    """Get students enrolled in a course"""
    try:
        teacher = request.user.teachers
        students = TeacherDashboardService.get_course_students(teacher, course_id)
        serializer = TeacherCourseStudentSerializer(students, many=True)
        return success_response(data=serializer.data, message="Students retrieved")
    except ValueError as e:
        return error_response(message=str(e), status_code=status.HTTP_403_FORBIDDEN)
    except Exception as e:
        return error_response(
            message=f"Error: {str(e)}",
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )


@api_view(["POST"])
@permission_classes([IsAuthenticated, IsTeacher])
def enter_grade(request, course_id):
    """Enter grade for a student"""
    try:
        teacher = request.user.teachers
        serializer = GradeEntrySerializer(data=request.data)

        if serializer.is_valid():
            result = TeacherDashboardService.enter_grade(
                teacher=teacher,
                course_id=course_id,
                inscription_id=serializer.validated_data["inscription_id"],
                session_id=serializer.validated_data["session_id"],
                mark=serializer.validated_data["mark"],
            )
            result_serializer = ResultSerializer(result)
            return success_response(
                data=result_serializer.data, message="Grade entered successfully"
            )
        return error_response(message="Invalid data", errors=serializer.errors)

    except ValueError as e:
        return error_response(message=str(e), status_code=status.HTTP_403_FORBIDDEN)
    except Exception as e:
        return error_response(
            message=f"Error: {str(e)}",
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )


@api_view(["POST"])
@permission_classes([IsAuthenticated, IsTeacher])
def bulk_enter_grades(request, course_id):
    """Bulk enter grades for multiple students"""
    try:
        teacher = request.user.teachers
        serializer = BulkGradeEntrySerializer(data=request.data)

        if serializer.is_valid():
            results = TeacherDashboardService.bulk_enter_grades(
                teacher=teacher,
                course_id=course_id,
                session_id=serializer.validated_data["session_id"],
                grades_data=serializer.validated_data["grades"],
            )
            result_serializer = ResultSerializer(results, many=True)
            return success_response(
                data=result_serializer.data,
                message=f"{len(results)} grades entered successfully",
            )
        return error_response(message="Invalid data", errors=serializer.errors)

    except ValueError as e:
        return error_response(message=str(e), status_code=status.HTTP_403_FORBIDDEN)
    except Exception as e:
        return error_response(
            message=f"Error: {str(e)}",
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )


@api_view(["GET"])
@permission_classes([IsAuthenticated, IsTeacher])
def teacher_exams(request):
    """Get exams where teacher is supervisor"""
    try:
        teacher = request.user.teachers
        exam_supervisors = TeacherDashboardService.get_teacher_exams(teacher)
        serializer = TeacherExamSerializer(exam_supervisors, many=True)
        return success_response(data=serializer.data, message="Exams retrieved")
    except Exception as e:
        return error_response(
            message=f"Error: {str(e)}",
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )


@api_view(["GET"])
@permission_classes([IsAuthenticated, IsTeacher])
def teacher_schedule(request):
    """Get teacher teaching schedule"""
    try:
        teacher = request.user.teachers
        timetables = TeacherDashboardService.get_teacher_schedule(teacher)
        serializer = TeacherScheduleSerializer(timetables, many=True)
        return success_response(data=serializer.data, message="Schedule retrieved")
    except Exception as e:
        return error_response(
            message=f"Error: {str(e)}",
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )


@api_view(["GET", "POST"])
@permission_classes([IsAuthenticated, IsTeacher])
def teacher_payment_claims(request):
    """Get or submit payment claims"""
    try:
        teacher = request.user.teachers

        if request.method == "GET":
            claims = TeacherDashboardService.get_teacher_payment_claims(teacher)
            serializer = TeacherPaymentClaimSerializer(claims, many=True)
            return success_response(
                data=serializer.data, message="Payment claims retrieved"
            )

        elif request.method == "POST":
            serializer = TeacherPaymentClaimSerializer(data=request.data)
            if serializer.is_valid():
                claim = TeacherDashboardService.submit_payment_claim(
                    teacher=teacher,
                    course_id=serializer.validated_data["course"],
                    hours_taught=serializer.validated_data["hours_taught"],
                    hourly_rate=serializer.validated_data["hourly_rate"],
                    total_amount=serializer.validated_data["total_amount"],
                )
                claim_serializer = TeacherPaymentClaimSerializer(claim)
                return success_response(
                    data=claim_serializer.data, message="Payment claim submitted"
                )
            return error_response(message="Invalid data", errors=serializer.errors)

    except ValueError as e:
        return error_response(message=str(e), status_code=status.HTTP_400_BAD_REQUEST)
    except Exception as e:
        return error_response(
            message=f"Error: {str(e)}",
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )


@api_view(["POST"])
@permission_classes([IsAuthenticated, IsTeacher])
def record_attendance(request, course_id):
    """Record student attendance"""
    try:
        teacher = request.user.teachers
        serializer = AttendanceEntrySerializer(data=request.data)

        if serializer.is_valid():
            attendance = TeacherDashboardService.record_attendance(
                teacher=teacher,
                course_id=course_id,
                inscription_id=serializer.validated_data["inscription_id"],
                attendance_date=serializer.validated_data["attendance_date"],
                status=serializer.validated_data["status"],
                notes=serializer.validated_data.get("notes", ""),
            )
            attendance_serializer = AttendanceRecordSerializer(attendance)
            return success_response(
                data=attendance_serializer.data, message="Attendance recorded"
            )
        return error_response(message="Invalid data", errors=serializer.errors)

    except ValueError as e:
        return error_response(message=str(e), status_code=status.HTTP_403_FORBIDDEN)
    except Exception as e:
        return error_response(
            message=f"Error: {str(e)}",
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )


@api_view(["GET"])
@permission_classes([IsAuthenticated, IsTeacher])
def course_attendance(request, course_id):
    """Get attendance records for a course"""
    try:
        teacher = request.user.teachers
        attendance_records = TeacherDashboardService.get_course_attendance(
            teacher, course_id
        )
        serializer = AttendanceRecordSerializer(attendance_records, many=True)
        return success_response(
            data=serializer.data, message="Attendance records retrieved"
        )
    except ValueError as e:
        return error_response(message=str(e), status_code=status.HTTP_403_FORBIDDEN)
    except Exception as e:
        return error_response(
            message=f"Error: {str(e)}",
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )


@api_view(["GET", "POST"])
@permission_classes([IsAuthenticated, IsTeacher])
def teacher_notifications(request):
    """Get or mark notifications as read"""
    try:
        teacher = request.user.teachers

        if request.method == "GET":
            notifications = TeacherDashboardService.get_teacher_notifications(teacher)
            serializer = TeacherNotificationSerializer(notifications, many=True)
            return success_response(
                data=serializer.data, message="Notifications retrieved"
            )

        elif request.method == "POST":
            notification_id = request.data.get("notification_id")
            if notification_id:
                TeacherDashboardService.mark_notification_read(notification_id, teacher)
                return success_response(message="Notification marked as read")
            return error_response(message="Notification ID required")

    except Exception as e:
        return error_response(
            message=f"Error: {str(e)}",
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )


@api_view(["GET", "POST"])
@permission_classes([IsAuthenticated, IsTeacher])
def teacher_messages(request):
    """Get or send messages"""
    try:
        teacher = request.user.teachers

        if request.method == "GET":
            messages = TeacherDashboardService.get_teacher_messages(teacher)
            serializer = TeacherMessageSerializer(messages, many=True)
            return success_response(data=serializer.data, message="Messages retrieved")

        elif request.method == "POST":
            serializer = TeacherMessageSerializer(data=request.data)
            if serializer.is_valid():
                message = TeacherDashboardService.send_message(
                    teacher=teacher,
                    recipient_id=serializer.validated_data["recipient"],
                    subject=serializer.validated_data["subject"],
                    content=serializer.validated_data["content"],
                    message_type=serializer.validated_data["message_type"],
                )
                message_serializer = TeacherMessageSerializer(message)
                return success_response(
                    data=message_serializer.data, message="Message sent"
                )
            return error_response(message="Invalid data", errors=serializer.errors)

    except Exception as e:
        return error_response(
            message=f"Error: {str(e)}",
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )


@api_view(["GET"])
@permission_classes([IsAuthenticated, IsTeacher])
def teaching_statistics(request):
    """Get teaching statistics"""
    try:
        teacher = request.user.teachers
        stats = TeacherDashboardService.get_teaching_statistics(teacher)
        serializer = TeachingStatisticsSerializer(stats)
        return success_response(
            data=serializer.data, message="Teaching statistics retrieved"
        )
    except Exception as e:
        return error_response(
            message=f"Error: {str(e)}",
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )
