from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated

from core.response_handler import error_response, success_response
from services.dependent_service.exam_module.exam_app.models import Exam

from .models import GradeComplaint, JurySession, OfficialDocument, TeacherPaymentClaim
from .serializers import (
    AcademicSecretaryStatsSerializer,
    ExamAttendanceSerializer,
    ExamSerializer,
    GradeComplaintSerializer,
    GradeEntryStatusSerializer,
    JuryDecisionSerializer,
    JurySessionSerializer,
    OfficialDocumentSerializer,
    TeacherPaymentClaimSerializer,
)
from .services import AcademicSecretaryService


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def academic_secretary_overview(request):
    """Get academic secretary dashboard overview"""
    try:
        stats = AcademicSecretaryService.get_dashboard_stats()
        serializer = AcademicSecretaryStatsSerializer(stats)
        return success_response(
            data=serializer.data, message="Academic secretary overview retrieved"
        )
    except Exception as e:
        return error_response(
            message=f"Error: {str(e)}",
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )


@api_view(["GET", "POST"])
@permission_classes([IsAuthenticated])
def exam_sessions(request):
    """Manage exam sessions"""
    try:
        if request.method == "GET":
            exams = Exam.objects.select_related("course").order_by("exam_date")
            serializer = ExamSerializer(exams, many=True)
            return success_response(
                data=serializer.data, message="Exam sessions retrieved"
            )

        elif request.method == "POST":
            course_id = request.data.get("course_id")
            exam_date = request.data.get("exam_date")
            duration = request.data.get("duration_minutes")
            room = request.data.get("room")
            supervisor_ids = request.data.get("supervisor_ids", [])

            exam = AcademicSecretaryService.schedule_exam(
                course_id, exam_date, duration, room, supervisor_ids, request.user
            )

            serializer = ExamSerializer(exam)
            return success_response(
                data=serializer.data, message="Exam session scheduled"
            )
    except Exception as e:
        return error_response(
            message=f"Error: {str(e)}",
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )


@api_view(["POST"])
@permission_classes([IsAuthenticated])
def record_exam_attendance(request, exam_id):
    """Record student exam attendance"""
    try:
        student_id = request.data.get("student_id")
        attendance_status = request.data.get("status")
        incident_notes = request.data.get("incident_notes", "")

        attendance = AcademicSecretaryService.record_exam_attendance(
            exam_id, student_id, attendance_status, incident_notes, request.user
        )

        serializer = ExamAttendanceSerializer(attendance)
        return success_response(
            data=serializer.data, message="Exam attendance recorded"
        )
    except Exception as e:
        return error_response(
            message=f"Error: {str(e)}",
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def grade_entry_status(request):
    """Check grade entry completion status by teachers"""
    try:
        grade_status = AcademicSecretaryService.check_grade_entry_status()
        serializer = GradeEntryStatusSerializer(grade_status, many=True)
        return success_response(
            data=serializer.data, message="Grade entry status retrieved"
        )
    except Exception as e:
        return error_response(
            message=f"Error: {str(e)}",
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )


@api_view(["GET", "POST"])
@permission_classes([IsAuthenticated])
def jury_sessions(request):
    """Manage jury sessions"""
    try:
        if request.method == "GET":
            juries = JurySession.objects.all().order_by("session_date")
            serializer = JurySessionSerializer(juries, many=True)
            return success_response(
                data=serializer.data, message="Jury sessions retrieved"
            )

        elif request.method == "POST":
            session_name = request.data.get("session_name")
            session_date = request.data.get("session_date")
            jury_member_ids = request.data.get("jury_member_ids", [])

            jury = AcademicSecretaryService.create_jury_session(
                session_name, session_date, jury_member_ids, request.user
            )

            serializer = JurySessionSerializer(jury)
            return success_response(
                data=serializer.data, message="Jury session created"
            )
    except Exception as e:
        return error_response(
            message=f"Error: {str(e)}",
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )


@api_view(["POST"])
@permission_classes([IsAuthenticated])
def record_jury_decision(request, jury_id):
    """Record jury decision for student"""
    try:
        student_id = request.data.get("student_id")
        decision = request.data.get("decision")
        notes = request.data.get("notes", "")

        jury_decision = AcademicSecretaryService.record_jury_decision(
            jury_id, student_id, decision, notes, request.user
        )

        serializer = JuryDecisionSerializer(jury_decision)
        return success_response(data=serializer.data, message="Jury decision recorded")
    except Exception as e:
        return error_response(
            message=f"Error: {str(e)}",
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def grade_complaints(request):
    """Get grade complaints"""
    try:
        complaints = GradeComplaint.objects.select_related(
            "student__user", "course", "assigned_to"
        ).order_by("-submitted_at")

        serializer = GradeComplaintSerializer(complaints, many=True)
        return success_response(
            data=serializer.data, message="Grade complaints retrieved"
        )
    except Exception as e:
        return error_response(
            message=f"Error: {str(e)}",
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )


@api_view(["POST"])
@permission_classes([IsAuthenticated])
def assign_complaint(request, complaint_id):
    """Assign grade complaint to teacher or department head"""
    try:
        assigned_to_id = request.data.get("assigned_to_id")

        complaint = AcademicSecretaryService.assign_grade_complaint(
            complaint_id, assigned_to_id, request.user
        )

        serializer = GradeComplaintSerializer(complaint)
        return success_response(data=serializer.data, message="Complaint assigned")
    except Exception as e:
        return error_response(
            message=f"Error: {str(e)}",
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )


@api_view(["POST"])
@permission_classes([IsAuthenticated])
def resolve_complaint(request, complaint_id):
    """Resolve grade complaint"""
    try:
        new_grade = request.data.get("new_grade")
        resolution_notes = request.data.get("resolution_notes", "")

        complaint = AcademicSecretaryService.resolve_grade_complaint(
            complaint_id, new_grade, resolution_notes, request.user
        )

        serializer = GradeComplaintSerializer(complaint)
        return success_response(data=serializer.data, message="Complaint resolved")
    except Exception as e:
        return error_response(
            message=f"Error: {str(e)}",
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )


@api_view(["GET", "POST"])
@permission_classes([IsAuthenticated])
def official_documents(request):
    """Manage official documents"""
    try:
        if request.method == "GET":
            documents = OfficialDocument.objects.select_related(
                "created_by", "signed_by"
            ).order_by("-created_at")

            serializer = OfficialDocumentSerializer(documents, many=True)
            return success_response(
                data=serializer.data, message="Official documents retrieved"
            )

        elif request.method == "POST":
            doc_type = request.data.get("document_type")
            title = request.data.get("title")
            content = request.data.get("content")

            document = AcademicSecretaryService.create_official_document(
                doc_type, title, content, request.user
            )

            serializer = OfficialDocumentSerializer(document)
            return success_response(
                data=serializer.data, message="Official document created"
            )
    except Exception as e:
        return error_response(
            message=f"Error: {str(e)}",
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )


@api_view(["POST"])
@permission_classes([IsAuthenticated])
def sign_document(request, document_id):
    """Sign official document"""
    try:
        document = AcademicSecretaryService.sign_document(document_id, request.user)
        serializer = OfficialDocumentSerializer(document)
        return success_response(data=serializer.data, message="Document signed")
    except Exception as e:
        return error_response(
            message=f"Error: {str(e)}",
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def payment_claims(request):
    """Get teacher payment claims"""
    try:
        claims = TeacherPaymentClaim.objects.select_related(
            "teacher__user", "course"
        ).order_by("-submitted_at")

        serializer = TeacherPaymentClaimSerializer(claims, many=True)
        return success_response(
            data=serializer.data, message="Payment claims retrieved"
        )
    except Exception as e:
        return error_response(
            message=f"Error: {str(e)}",
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )


@api_view(["POST"])
@permission_classes([IsAuthenticated])
def verify_payment_claim(request, claim_id):
    """Verify teacher payment claim"""
    try:
        claim = AcademicSecretaryService.verify_payment_claim(claim_id, request.user)
        serializer = TeacherPaymentClaimSerializer(claim)
        return success_response(data=serializer.data, message="Payment claim verified")
    except Exception as e:
        return error_response(
            message=f"Error: {str(e)}",
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )


@api_view(["POST"])
@permission_classes([IsAuthenticated])
def approve_payment_claim(request, claim_id):
    """Approve payment claim"""
    try:
        claim = AcademicSecretaryService.approve_payment_claim(claim_id, request.user)
        serializer = TeacherPaymentClaimSerializer(claim)
        return success_response(data=serializer.data, message="Payment claim approved")
    except Exception as e:
        return error_response(
            message=f"Error: {str(e)}",
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )


@api_view(["POST"])
@permission_classes([IsAuthenticated])
def send_claim_to_finance(request, claim_id):
    """Send approved claim to financial service"""
    try:
        claim = AcademicSecretaryService.send_claim_to_finance(claim_id, request.user)
        serializer = TeacherPaymentClaimSerializer(claim)
        return success_response(data=serializer.data, message="Claim sent to finance")
    except Exception as e:
        return error_response(
            message=f"Error: {str(e)}",
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )
