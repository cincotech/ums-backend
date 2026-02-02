from django.db.models import Q
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import OrderingFilter, SearchFilter
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated

from core.permissions import (
    CanRequestDocuments,
    CanSendMessages,
    CanViewGrades,
    CanViewTranscript,
    IsStudent,
)
from core.response_handler import error_response, success_response

from .serializers import (
    AcademicProgressSerializer,
    StudentAttendanceSerializer,
    StudentDashboardStatsSerializer,
    StudentDocumentRequestSerializer,
    StudentExamSerializer,
    StudentGradeComplaintSerializer,
    StudentGradesSerializer,
    StudentJuryDecisionSerializer,
    StudentMessageSerializer,
    StudentNotificationSerializer,
    StudentOfficialDocumentSerializer,
    StudentPaymentInfoSerializer,
    StudentProfileSerializer,
    StudentScheduleSerializer,
    StudentTranscriptSerializer,
    StudentTimetableMergeSerializer,
    StudentTimetableSerializer,
    
)
from .services import StudentDashboardService


@api_view(["GET"])
@permission_classes([IsAuthenticated, IsStudent])
def student_dashboard_overview(request):
    """Get student dashboard overview"""
    try:
        student = request.user.students_users
        stats = StudentDashboardService.get_student_dashboard_stats(student)
        serializer = StudentDashboardStatsSerializer(stats)
        return success_response(
            data=serializer.data, message="Student dashboard overview retrieved"
        )
    except Exception as e:
        return error_response(
            message=f"Error: {str(e)}",
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )


@api_view(["GET", "PUT"])
@permission_classes([IsAuthenticated, IsStudent])
def student_profile(request):
    """Get or update student profile"""
    try:
        student = request.user.students_users

        if request.method == "GET":
            profile_data = StudentDashboardService.get_student_profile(student)
            serializer = StudentProfileSerializer(profile_data)
            return success_response(
                data=serializer.data, message="Student profile retrieved"
            )

        elif request.method == "PUT":
            serializer = StudentProfileSerializer(data=request.data)
            if serializer.is_valid():
                updated_profile = StudentDashboardService.update_profile(
                    student, serializer.validated_data
                )
                serializer = StudentProfileSerializer(updated_profile)
                return success_response(
                    data=serializer.data, message="Student profile updated"
                )
            return error_response(message="Invalid data", errors=serializer.errors)

    except Exception as e:
        return error_response(
            message=f"Error: {str(e)}",
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )


@api_view(["GET"])
@permission_classes([IsAuthenticated, IsStudent, CanViewGrades])
def student_grades(request):
    """Get student grades with payment condition"""
    try:
        student = request.user.students_users
        grades_data = StudentDashboardService.get_student_grades(student)

        if isinstance(grades_data, dict) and "error" in grades_data:
            return error_response(
                message=grades_data["message"],
                status_code=status.HTTP_402_PAYMENT_REQUIRED,
            )

        serializer = StudentGradesSerializer(grades_data, many=True)
        return success_response(
            data=serializer.data, message="Student grades retrieved"
        )
    except Exception as e:
        return error_response(
            message=f"Error: {str(e)}",
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )


@api_view(["GET"])
@permission_classes([IsAuthenticated, IsStudent, CanViewTranscript])
def student_transcript(request):
    """Get student transcript"""
    try:
        student = request.user.students_users
        transcript_data = StudentDashboardService.get_student_transcript(student)

        if isinstance(transcript_data, dict) and "error" in transcript_data:
            return error_response(
                message=transcript_data["message"],
                status_code=status.HTTP_403_FORBIDDEN,
            )

        serializer = StudentTranscriptSerializer(transcript_data)
        return success_response(
            data=serializer.data, message="Student transcript retrieved"
        )
    except Exception as e:
        return error_response(
            message=f"Error: {str(e)}",
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )


@api_view(["GET"])
@permission_classes([IsAuthenticated, IsStudent])
def academic_progress(request):
    """Get student academic progress"""
    try:
        student = request.user.students_users
        progress_data = StudentDashboardService.get_academic_progress(student)
        serializer = AcademicProgressSerializer(progress_data)
        return success_response(
            data=serializer.data, message="Academic progress retrieved"
        )
    except Exception as e:
        return error_response(
            message=f"Error: {str(e)}",
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )


@api_view(["GET"])
@permission_classes([IsAuthenticated, IsStudent])
def student_schedule(request):
    """Get student schedule: current day and full week"""
    try:
        student = request.user.students_users
        schedule_data = StudentDashboardService.get_student_schedule(student)
        
        response_data = {}
        
        if schedule_data['day_of_week']:
            response_data['day_of_week'] = StudentTimetableSerializer(schedule_data['day_of_week']).data
        else:
            response_data['day_of_week'] = None
            
        if schedule_data['merge']:
            response_data['merge'] = StudentTimetableMergeSerializer(schedule_data['merge'], many=True).data
        else:
            response_data['merge'] = []
        
        return success_response(
            data=response_data,
            message="Student schedule retrieved"
        )
    except Exception as e:
        return error_response(
            message=f"Error: {str(e)}",
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )


@api_view(["GET"])
@permission_classes([IsAuthenticated, IsStudent])
def student_attendance(request):
    """Get student attendance"""
    try:
        student = request.user.students_users
        attendance_data = StudentDashboardService.get_student_attendance(student)
        serializer = StudentAttendanceSerializer(attendance_data, many=True)
        return success_response(
            data=serializer.data, message="Student attendance retrieved"
        )
    except Exception as e:
        return error_response(
            message=f"Error: {str(e)}",
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )


@api_view(["GET", "POST"])
@permission_classes([IsAuthenticated, IsStudent])
def student_notifications(request):
    """Get or mark notifications as read"""
    try:
        student = request.user.students_users

        if request.method == "GET":
            notifications = StudentDashboardService.get_student_notifications(student)
            serializer = StudentNotificationSerializer(notifications, many=True)
            return success_response(
                data=serializer.data, message="Student notifications retrieved"
            )

        elif request.method == "POST":
            notification_id = request.data.get("notification_id")
            if notification_id:
                StudentDashboardService.mark_notification_read(notification_id)
                return success_response(message="Notification marked as read")
            return error_response(message="Notification ID required")

    except Exception as e:
        return error_response(
            message=f"Error: {str(e)}",
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )


@api_view(["GET", "POST"])
@permission_classes([IsAuthenticated, IsStudent, CanRequestDocuments])
def document_requests(request):
    """Get or create document requests"""
    try:
        student = request.user.students_users

        if request.method == "GET":
            requests = StudentDashboardService.get_document_requests(student)
            serializer = StudentDocumentRequestSerializer(requests, many=True)
            return success_response(
                data=serializer.data, message="Document requests retrieved"
            )

        elif request.method == "POST":
            serializer = StudentDocumentRequestSerializer(data=request.data)
            if serializer.is_valid():
                request_obj = StudentDashboardService.request_document(
                    student, serializer.validated_data
                )
                serializer = StudentDocumentRequestSerializer(request_obj)
                return success_response(
                    data=serializer.data, message="Document request created"
                )
            return error_response(message="Invalid data", errors=serializer.errors)

    except Exception as e:
        return error_response(
            message=f"Error: {str(e)}",
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )


@api_view(["GET", "POST"])
@permission_classes([IsAuthenticated, IsStudent, CanSendMessages])
def student_messages(request):
    """Get or send messages"""
    try:
        student = request.user.students_users

        if request.method == "GET":
            messages = StudentDashboardService.get_student_messages(student)
            serializer = StudentMessageSerializer(messages, many=True)
            return success_response(
                data=serializer.data, message="Student messages retrieved"
            )

        elif request.method == "POST":
            serializer = StudentMessageSerializer(data=request.data)
            if serializer.is_valid():
                message = StudentDashboardService.send_message(
                    student, serializer.validated_data
                )
                serializer = StudentMessageSerializer(message)
                return success_response(data=serializer.data, message="Message sent")
            return error_response(message="Invalid data", errors=serializer.errors)

    except Exception as e:
        return error_response(
            message=f"Error: {str(e)}",
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )


@api_view(["GET"])
@permission_classes([IsAuthenticated, IsStudent])
def download_documents(request):
    """Download available documents"""
    try:
        student = request.user.students_users
        document_type = request.query_params.get("type")

        if not document_type:
            return error_response(message="Document type required")

        document_data = StudentDashboardService.get_downloadable_document(
            student, document_type
        )

        if isinstance(document_data, dict) and "error" in document_data:
            return error_response(
                message=document_data["message"], status_code=status.HTTP_403_FORBIDDEN
            )

        # Return document data (would typically return file response)
        return success_response(data=document_data, message="Document retrieved")

    except Exception as e:
        return error_response(
            message=f"Error: {str(e)}",
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )


@api_view(["GET"])
@permission_classes([IsAuthenticated, IsStudent])
def student_jury_decisions(request):
    """Get jury decisions for student"""
    try:
        student = request.user.students_users
        decisions = StudentDashboardService.get_student_jury_decisions(student)
        serializer = StudentJuryDecisionSerializer(decisions, many=True)
        return success_response(
            data=serializer.data, message="Jury decisions retrieved"
        )
    except Exception as e:
        return error_response(
            message=f"Error: {str(e)}",
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )


@api_view(["GET", "POST"])
@permission_classes([IsAuthenticated, IsStudent])
def student_grade_complaints(request):
    """Get or submit grade complaints"""
    try:
        student = request.user.students_users

        if request.method == "GET":
            complaints = StudentDashboardService.get_student_grade_complaints(student)
            serializer = StudentGradeComplaintSerializer(complaints, many=True)
            return success_response(
                data=serializer.data, message="Grade complaints retrieved"
            )

        elif request.method == "POST":
            serializer = StudentGradeComplaintSerializer(data=request.data)
            if serializer.is_valid():
                complaint = StudentDashboardService.submit_grade_complaint(
                    student=student,
                    course_id=serializer.validated_data["course_id"],
                    original_grade=serializer.validated_data["original_grade"],
                    complaint_reason=serializer.validated_data["complaint_reason"],
                )
                serializer = StudentGradeComplaintSerializer(complaint)
                return success_response(
                    data=serializer.data, message="Grade complaint submitted"
                )
            return error_response(message="Invalid data", errors=serializer.errors)

    except ValueError as e:
        return error_response(message=str(e), status_code=status.HTTP_400_BAD_REQUEST)
    except Exception as e:
        return error_response(
            message=f"Error: {str(e)}",
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )


@api_view(["GET"])
@permission_classes([IsAuthenticated, IsStudent])
def student_exams(request):
    """Get upcoming exams for student"""
    try:
        student = request.user.students_users
        exams = StudentDashboardService.get_student_exams(student)
        serializer = StudentExamSerializer(exams, many=True)
        return success_response(data=serializer.data, message="Exams retrieved")
    except Exception as e:
        return error_response(
            message=f"Error: {str(e)}",
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )


@api_view(["GET"])
@permission_classes([IsAuthenticated, IsStudent])
def student_official_documents(request):
    """Get official documents (circulars, service notes)"""
    try:
        student = request.user.students_users
        documents = StudentDashboardService.get_official_documents(student)
        serializer = StudentOfficialDocumentSerializer(documents, many=True)
        return success_response(
            data=serializer.data, message="Official documents retrieved"
        )
    except Exception as e:
        return error_response(
            message=f"Error: {str(e)}",
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )


@api_view(["GET"])
@permission_classes([IsAuthenticated, IsStudent, CanViewGrades])
def student_payments(request):
    """Get student payment history with installments"""
    try:
        student = request.user.students_users
        payment_data = StudentDashboardService.get_student_payments(student)
        
        serializer = StudentPaymentInfoSerializer(payment_data)
        return success_response(data=serializer.data, message="Payment information retrieved")
    except Exception as e:
        return error_response(
            message=f"Error: {str(e)}",
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )
