from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated

from core.response_handler import error_response, success_response

from .models import (
    AbsenceJustification,
    CounselingSession,
    DocumentRequest,
    Scholarship,
    StudentActivity,
)
from .serializers import (
    AbsenceJustificationSerializer,
    CounselingSessionSerializer,
    DocumentRequestSerializer,
    ScholarshipSerializer,
    StudentActivitySerializer,
    StudentReportSerializer,
    StudentServicesStatsSerializer,
)
from .services import StudentServicesService


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def student_services_overview(request):
    """Get student services dashboard overview"""
    try:
        stats = StudentServicesService.get_dashboard_stats()
        serializer = StudentServicesStatsSerializer(stats)
        return success_response(
            data=serializer.data, message="Student services overview retrieved"
        )
    except Exception as e:
        return error_response(
            message=f"Error: {str(e)}",
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )


@api_view(["GET", "POST"])
@permission_classes([IsAuthenticated])
def document_requests(request):
    """Manage document requests"""
    try:
        if request.method == "GET":
            requests_qs = DocumentRequest.objects.select_related(
                "student__user"
            ).order_by("-requested_at")
            serializer = DocumentRequestSerializer(requests_qs, many=True)
            return success_response(
                data=serializer.data, message="Document requests retrieved"
            )

        elif request.method == "POST":
            serializer = DocumentRequestSerializer(data=request.data)
            if serializer.is_valid():
                serializer.save()
                return success_response(
                    data=serializer.data, message="Document request created"
                )
            return error_response(message="Invalid data", errors=serializer.errors)
    except Exception as e:
        return error_response(
            message=f"Error: {str(e)}",
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )


@api_view(["POST"])
@permission_classes([IsAuthenticated])
def process_document_request(request, request_id):
    """Process document request (approve/reject/complete)"""
    try:
        action = request.data.get("action")  # processing, ready, delivered, rejected
        notes = request.data.get("notes", "")

        doc_request = StudentServicesService.process_document_request(
            request_id, action, notes, request.user
        )

        serializer = DocumentRequestSerializer(doc_request)
        return success_response(
            data=serializer.data, message=f"Document request {action}"
        )
    except Exception as e:
        return error_response(
            message=f"Error: {str(e)}",
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )


@api_view(["GET", "POST"])
@permission_classes([IsAuthenticated])
def absence_justifications(request):
    """Manage absence justifications"""
    try:
        if request.method == "GET":
            absences = AbsenceJustification.objects.select_related(
                "student__user"
            ).order_by("-submitted_at")
            serializer = AbsenceJustificationSerializer(absences, many=True)
            return success_response(
                data=serializer.data, message="Absence justifications retrieved"
            )

        elif request.method == "POST":
            serializer = AbsenceJustificationSerializer(data=request.data)
            if serializer.is_valid():
                serializer.save()
                return success_response(
                    data=serializer.data, message="Absence justification submitted"
                )
            return error_response(message="Invalid data", errors=serializer.errors)
    except Exception as e:
        return error_response(
            message=f"Error: {str(e)}",
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )


@api_view(["POST"])
@permission_classes([IsAuthenticated])
def process_absence_justification(request, absence_id):
    """Process absence justification (approve/reject)"""
    try:
        decision = request.data.get("decision")  # approved, rejected

        absence = StudentServicesService.process_absence_justification(
            absence_id, decision, request.user
        )

        serializer = AbsenceJustificationSerializer(absence)
        return success_response(
            data=serializer.data, message=f"Absence justification {decision}"
        )
    except Exception as e:
        return error_response(
            message=f"Error: {str(e)}",
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )


@api_view(["GET", "POST"])
@permission_classes([IsAuthenticated])
def student_activities(request):
    """Manage student activities and clubs"""
    try:
        if request.method == "GET":
            activities = StudentActivity.objects.select_related(
                "organizer__user"
            ).order_by("-created_at")
            serializer = StudentActivitySerializer(activities, many=True)
            return success_response(
                data=serializer.data, message="Student activities retrieved"
            )

        elif request.method == "POST":
            serializer = StudentActivitySerializer(data=request.data)
            if serializer.is_valid():
                serializer.save()
                return success_response(
                    data=serializer.data, message="Student activity created"
                )
            return error_response(message="Invalid data", errors=serializer.errors)
    except Exception as e:
        return error_response(
            message=f"Error: {str(e)}",
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )


@api_view(["POST"])
@permission_classes([IsAuthenticated])
def approve_student_activity(request, activity_id):
    """Approve student club/activity"""
    try:
        activity = StudentServicesService.approve_student_activity(
            activity_id, request.user
        )
        serializer = StudentActivitySerializer(activity)
        return success_response(
            data=serializer.data, message="Student activity approved"
        )
    except Exception as e:
        return error_response(
            message=f"Error: {str(e)}",
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )


@api_view(["GET", "POST"])
@permission_classes([IsAuthenticated])
def scholarships(request):
    """Manage student scholarships"""
    try:
        if request.method == "GET":
            scholarships_qs = Scholarship.objects.select_related(
                "student__user"
            ).order_by("-created_at")
            serializer = ScholarshipSerializer(scholarships_qs, many=True)
            return success_response(
                data=serializer.data, message="Scholarships retrieved"
            )

        elif request.method == "POST":
            student_id = request.data.get("student_id")
            scholarship = StudentServicesService.manage_scholarship(
                student_id, request.data, request.user
            )
            serializer = ScholarshipSerializer(scholarship)
            return success_response(data=serializer.data, message="Scholarship added")
    except Exception as e:
        return error_response(
            message=f"Error: {str(e)}",
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )


@api_view(["GET", "POST"])
@permission_classes([IsAuthenticated])
def counseling_sessions(request):
    """Manage counseling and orientation sessions"""
    try:
        if request.method == "GET":
            sessions = CounselingSession.objects.select_related("counselor").order_by(
                "-scheduled_date"
            )
            serializer = CounselingSessionSerializer(sessions, many=True)
            return success_response(
                data=serializer.data, message="Counseling sessions retrieved"
            )

        elif request.method == "POST":
            session = StudentServicesService.schedule_counseling_session(
                request.data, request.user
            )
            serializer = CounselingSessionSerializer(session)
            return success_response(
                data=serializer.data, message="Counseling session scheduled"
            )
    except Exception as e:
        return error_response(
            message=f"Error: {str(e)}",
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def enrollment_reports(request):
    """Generate enrollment statistics and reports"""
    try:
        academic_year = request.GET.get("academic_year")
        report = StudentServicesService.generate_enrollment_report(academic_year)
        serializer = StudentReportSerializer(report)
        return success_response(
            data=serializer.data, message="Enrollment report generated"
        )
    except Exception as e:
        return error_response(
            message=f"Error: {str(e)}",
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def student_population_data(request):
    """Get student population data by year and class"""
    try:
        population_data = StudentServicesService.get_student_population_data()
        return success_response(
            data=population_data, message="Student population data retrieved"
        )
    except Exception as e:
        return error_response(
            message=f"Error: {str(e)}",
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )


@api_view(["PUT"])
@permission_classes([IsAuthenticated])
def update_student_profile(request, student_id):
    """Update student personal and administrative information"""
    try:
        student = StudentServicesService.update_student_profile(
            student_id, request.data, request.user
        )

        from services.foundational_service.auth_module.authentication_app.serializers import (
            UserSerializer,
        )

        serializer = UserSerializer(student.user)
        return success_response(data=serializer.data, message="Student profile updated")
    except Exception as e:
        return error_response(
            message=f"Error: {str(e)}",
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )
