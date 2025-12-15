from rest_framework import status, viewsets
from rest_framework.decorators import action, api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from core.permissions import IsAcademicSecretary
from core.response_handler import error_response, success_response

from .serializers import (
    AcademicSecretaryStatsSerializer,
    CompilationStatusSerializer,
    CourseResultSerializer,
    ExamRoomSerializer,
    ExamSerializer,
    ExamSupervisorSerializer,
    GradeComplaintSerializer,
    GradeEntryStatusSerializer,
    InscriptionSerializer,
    InscriptionStatisticsSerializer,
    JuryDecisionSerializer,
    JurySessionSerializer,
    OfficialDocumentSerializer,
    TeacherPaymentClaimSerializer,
)
from .services import AcademicSecretaryService

# ==================== DASHBOARD ====================


@api_view(["GET"])
@permission_classes([IsAuthenticated, IsAcademicSecretary])
def dashboard_stats(request):
    """Get academic secretary dashboard statistics"""
    try:
        stats = AcademicSecretaryService.get_dashboard_stats()
        serializer = AcademicSecretaryStatsSerializer(stats)
        return success_response(
            data=serializer.data, message="Dashboard stats retrieved"
        )
    except Exception as e:
        return error_response(
            message=f"Error: {str(e)}",
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )


# ==================== EXAM MANAGEMENT ====================


class ExamViewSet(viewsets.ModelViewSet):
    """ViewSet for managing exams"""

    serializer_class = ExamSerializer
    permission_classes = [IsAuthenticated, IsAcademicSecretary]

    def get_queryset(self):
        filters = {}
        if self.request.query_params.get("status"):
            filters["status"] = self.request.query_params.get("status")
        if self.request.query_params.get("course_id"):
            filters["course_id"] = self.request.query_params.get("course_id")
        if self.request.query_params.get("start_date_from"):
            filters["start_date_from"] = self.request.query_params.get(
                "start_date_from"
            )
        if self.request.query_params.get("start_date_to"):
            filters["start_date_to"] = self.request.query_params.get("start_date_to")

        return AcademicSecretaryService.get_exam_list(filters if filters else None)

    def create(self, request, *args, **kwargs):
        try:
            exam = AcademicSecretaryService.schedule_exam(
                course_id=request.data.get("course"),
                exam_type_id=request.data.get("exam_type"),
                start_date=request.data.get("start_date"),
                end_date=request.data.get("end_date"),
                duration_minutes=request.data.get("duration_minutes"),
                max_marks=request.data.get("max_marks"),
                instructions=request.data.get("instructions", ""),
                created_by=request.user,
            )
            serializer = self.get_serializer(exam)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        except Exception as e:
            return Response(
                {"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    @action(detail=True, methods=["post"])
    def update_status(self, request, pk=None):
        """Update exam status"""
        try:
            exam = AcademicSecretaryService.update_exam_status(
                pk, request.data.get("status")
            )
            serializer = self.get_serializer(exam)
            return Response(serializer.data)
        except ValueError as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response(
                {"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    @action(detail=True, methods=["post"])
    def assign_room(self, request, pk=None):
        """Assign room to exam"""
        try:
            exam_room = AcademicSecretaryService.assign_exam_room(
                exam_id=pk,
                room_id=request.data.get("room"),
                capacity=request.data.get("capacity"),
            )
            serializer = ExamRoomSerializer(exam_room)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        except Exception as e:
            return Response(
                {"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    @action(detail=True, methods=["post"])
    def assign_supervisor(self, request, pk=None):
        """Assign supervisor to exam"""
        try:
            exam_supervisor = AcademicSecretaryService.assign_exam_supervisor(
                exam_id=pk, supervisor_id=request.data.get("supervisor")
            )
            serializer = ExamSupervisorSerializer(exam_supervisor)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        except ValueError as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response(
                {"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


# ==================== GRADE MONITORING ====================


@api_view(["GET"])
@permission_classes([IsAuthenticated, IsAcademicSecretary])
def grade_entry_status(request):
    """Get grade entry completion status"""
    try:
        filters = {}
        if request.query_params.get("academic_year_id"):
            filters["academic_year_id"] = request.query_params.get("academic_year_id")

        grade_status = AcademicSecretaryService.check_grade_entry_status(
            filters if filters else None
        )
        serializer = GradeEntryStatusSerializer(grade_status, many=True)
        return success_response(
            data=serializer.data, message="Grade entry status retrieved"
        )
    except Exception as e:
        return error_response(
            message=f"Error: {str(e)}",
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )


@api_view(["GET"])
@permission_classes([IsAuthenticated, IsAcademicSecretary])
def course_results(request, course_id):
    """Get results for a specific course"""
    try:
        session_id = request.query_params.get("session_id")
        results = AcademicSecretaryService.get_course_results(course_id, session_id)
        serializer = CourseResultSerializer(results, many=True)
        return success_response(
            data=serializer.data, message="Course results retrieved"
        )
    except Exception as e:
        return error_response(
            message=f"Error: {str(e)}",
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )


# ==================== JURY MANAGEMENT ====================


class JurySessionViewSet(viewsets.ModelViewSet):
    """ViewSet for managing jury sessions"""

    serializer_class = JurySessionSerializer
    permission_classes = [IsAuthenticated, IsAcademicSecretary]

    def get_queryset(self):
        filters = {}
        if self.request.query_params.get("status"):
            filters["status"] = self.request.query_params.get("status")
        if self.request.query_params.get("date_from"):
            filters["date_from"] = self.request.query_params.get("date_from")
        if self.request.query_params.get("date_to"):
            filters["date_to"] = self.request.query_params.get("date_to")

        return AcademicSecretaryService.get_jury_sessions(filters if filters else None)

    def create(self, request, *args, **kwargs):
        try:
            jury = AcademicSecretaryService.create_jury_session(
                session_name=request.data.get("session_name"),
                session_date=request.data.get("session_date"),
                jury_member_ids=request.data.get("jury_members", []),
                created_by=request.user,
            )
            serializer = self.get_serializer(jury)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        except Exception as e:
            return Response(
                {"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    @action(detail=True, methods=["post"])
    def update_status(self, request, pk=None):
        """Update jury session status"""
        try:
            jury = AcademicSecretaryService.update_jury_status(
                jury_id=pk,
                status=request.data.get("status"),
                minutes_document=request.data.get("minutes_document"),
            )
            serializer = self.get_serializer(jury)
            return Response(serializer.data)
        except ValueError as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response(
                {"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    @action(detail=True, methods=["get"])
    def decisions(self, request, pk=None):
        """Get all decisions for a jury session"""
        try:
            decisions = AcademicSecretaryService.get_jury_decisions(pk)
            serializer = JuryDecisionSerializer(decisions, many=True)
            return Response(serializer.data)
        except Exception as e:
            return Response(
                {"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    @action(detail=True, methods=["post"])
    def record_decision(self, request, pk=None):
        """Record jury decision for a student"""
        try:
            decision = AcademicSecretaryService.record_jury_decision(
                jury_id=pk,
                student_id=request.data.get("student"),
                decision=request.data.get("decision"),
                notes=request.data.get("notes", ""),
                validated_by=request.user,
            )
            serializer = JuryDecisionSerializer(decision)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        except ValueError as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response(
                {"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


# ==================== GRADE COMPLAINT MANAGEMENT ====================


class GradeComplaintViewSet(viewsets.ModelViewSet):
    """ViewSet for managing grade complaints"""

    serializer_class = GradeComplaintSerializer
    permission_classes = [IsAuthenticated, IsAcademicSecretary]

    def get_queryset(self):
        filters = {}
        if self.request.query_params.get("status"):
            filters["status"] = self.request.query_params.get("status")
        if self.request.query_params.get("course_id"):
            filters["course_id"] = self.request.query_params.get("course_id")
        if self.request.query_params.get("student_id"):
            filters["student_id"] = self.request.query_params.get("student_id")

        return AcademicSecretaryService.get_grade_complaints(
            filters if filters else None
        )

    @action(detail=True, methods=["post"])
    def assign(self, request, pk=None):
        """Assign complaint to teacher"""
        try:
            complaint = AcademicSecretaryService.assign_grade_complaint(
                complaint_id=pk, assigned_to_id=request.data.get("assigned_to")
            )
            serializer = self.get_serializer(complaint)
            return Response(serializer.data)
        except ValueError as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response(
                {"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    @action(detail=True, methods=["post"])
    def update_status(self, request, pk=None):
        """Update complaint status"""
        try:
            complaint = AcademicSecretaryService.update_complaint_status(
                complaint_id=pk, status=request.data.get("status")
            )
            serializer = self.get_serializer(complaint)
            return Response(serializer.data)
        except ValueError as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response(
                {"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    @action(detail=True, methods=["post"])
    def resolve(self, request, pk=None):
        """Resolve grade complaint"""
        try:
            complaint = AcademicSecretaryService.resolve_grade_complaint(
                complaint_id=pk,
                new_grade=request.data.get("new_grade"),
                resolution_notes=request.data.get("resolution_notes", ""),
                resolved_by=request.user,
            )
            serializer = self.get_serializer(complaint)
            return Response(serializer.data)
        except ValueError as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response(
                {"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


# ==================== OFFICIAL DOCUMENT MANAGEMENT ====================


class OfficialDocumentViewSet(viewsets.ModelViewSet):
    """ViewSet for managing official documents"""

    serializer_class = OfficialDocumentSerializer
    permission_classes = [IsAuthenticated, IsAcademicSecretary]

    def get_queryset(self):
        filters = {}
        if self.request.query_params.get("document_type"):
            filters["document_type"] = self.request.query_params.get("document_type")
        if self.request.query_params.get("status"):
            filters["status"] = self.request.query_params.get("status")

        return AcademicSecretaryService.get_official_documents(
            filters if filters else None
        )

    def create(self, request, *args, **kwargs):
        try:
            document = AcademicSecretaryService.create_official_document(
                doc_type=request.data.get("document_type"),
                title=request.data.get("title"),
                content=request.data.get("content"),
                created_by=request.user,
            )
            serializer = self.get_serializer(document)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        except Exception as e:
            return Response(
                {"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    @action(detail=True, methods=["post"])
    def update_status(self, request, pk=None):
        """Update document status"""
        try:
            document = AcademicSecretaryService.update_document_status(
                document_id=pk, status=request.data.get("status")
            )
            serializer = self.get_serializer(document)
            return Response(serializer.data)
        except ValueError as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response(
                {"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    @action(detail=True, methods=["post"])
    def sign(self, request, pk=None):
        """Sign official document"""
        try:
            document = AcademicSecretaryService.sign_document(
                document_id=pk, signed_by=request.user
            )
            serializer = self.get_serializer(document)
            return Response(serializer.data)
        except ValueError as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response(
                {"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


# ==================== PAYMENT CLAIM MANAGEMENT ====================


class PaymentClaimViewSet(viewsets.ModelViewSet):
    """ViewSet for managing teacher payment claims"""

    serializer_class = TeacherPaymentClaimSerializer
    permission_classes = [IsAuthenticated, IsAcademicSecretary]

    def get_queryset(self):
        filters = {}
        if self.request.query_params.get("status"):
            filters["status"] = self.request.query_params.get("status")
        if self.request.query_params.get("teacher_id"):
            filters["teacher_id"] = self.request.query_params.get("teacher_id")
        if self.request.query_params.get("course_id"):
            filters["course_id"] = self.request.query_params.get("course_id")

        return AcademicSecretaryService.get_payment_claims(filters if filters else None)

    @action(detail=True, methods=["post"])
    def verify(self, request, pk=None):
        """Verify payment claim"""
        try:
            claim = AcademicSecretaryService.verify_payment_claim(
                claim_id=pk, verified_by=request.user
            )
            serializer = self.get_serializer(claim)
            return Response(serializer.data)
        except ValueError as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response(
                {"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    @action(detail=True, methods=["post"])
    def approve(self, request, pk=None):
        """Approve payment claim"""
        try:
            claim = AcademicSecretaryService.approve_payment_claim(
                claim_id=pk, approved_by=request.user
            )
            serializer = self.get_serializer(claim)
            return Response(serializer.data)
        except ValueError as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response(
                {"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    @action(detail=True, methods=["post"])
    def sign(self, request, pk=None):
        """Sign payment claim"""
        try:
            claim = AcademicSecretaryService.sign_payment_claim(
                claim_id=pk, signed_by=request.user
            )
            serializer = self.get_serializer(claim)
            return Response(serializer.data)
        except ValueError as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response(
                {"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    @action(detail=True, methods=["post"])
    def send_to_finance(self, request, pk=None):
        """Send claim to finance"""
        try:
            claim = AcademicSecretaryService.send_claim_to_finance(claim_id=pk)
            serializer = self.get_serializer(claim)
            return Response(serializer.data)
        except ValueError as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response(
                {"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    @action(detail=True, methods=["post"])
    def reject(self, request, pk=None):
        """Reject payment claim"""
        try:
            claim = AcademicSecretaryService.reject_payment_claim(
                claim_id=pk, rejection_reason=request.data.get("rejection_reason", "")
            )
            serializer = self.get_serializer(claim)
            return Response(serializer.data)
        except ValueError as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response(
                {"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


# ==================== INSCRIPTION MANAGEMENT ====================


class InscriptionViewSet(viewsets.ModelViewSet):
    """ViewSet for managing student inscriptions"""

    serializer_class = InscriptionSerializer
    permission_classes = [IsAuthenticated, IsAcademicSecretary]

    def get_queryset(self):
        filters = {}
        if self.request.query_params.get("status"):
            filters["status"] = self.request.query_params.get("status")
        if self.request.query_params.get("academic_year_id"):
            filters["academic_year_id"] = self.request.query_params.get(
                "academic_year_id"
            )
        if self.request.query_params.get("class_id"):
            filters["class_id"] = self.request.query_params.get("class_id")

        return AcademicSecretaryService.get_inscriptions(filters if filters else None)

    @action(detail=False, methods=["get"])
    def statistics(self, request):
        """Get inscription statistics"""
        try:
            academic_year_id = request.query_params.get("academic_year_id")
            stats = AcademicSecretaryService.get_inscription_statistics(
                academic_year_id
            )
            serializer = InscriptionStatisticsSerializer(stats)
            return Response(serializer.data)
        except Exception as e:
            return Response(
                {"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


# ==================== RESULT COMPILATION ====================


@api_view(["GET"])
@permission_classes([IsAuthenticated, IsAcademicSecretary])
def compilation_status(request):
    """Get result compilation status"""
    try:
        academic_year_id = request.query_params.get("academic_year_id")
        stats = AcademicSecretaryService.get_compilation_status(academic_year_id)
        serializer = CompilationStatusSerializer(stats)
        return success_response(
            data=serializer.data, message="Compilation status retrieved"
        )
    except Exception as e:
        return error_response(
            message=f"Error: {str(e)}",
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )
