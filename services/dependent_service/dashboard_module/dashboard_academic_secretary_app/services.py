import logging

from datetime import timedelta

from django.db import transaction
from django.db.models import Count
from django.utils import timezone

from services.core_service.academic_module.course_app.models import Course
from services.core_service.academic_module.teacher_app.models import Attribution
from services.core_service.student_module.inscription_app.models import Inscription
from services.dependent_service.dashboard_module.dashboard_shared_app.models import (
    Notification,
)
from services.dependent_service.exam_module.exam_app.models import (
    Exam,
    ExamRoom,
    ExamSupervisor,
)
from services.dependent_service.exam_module.result_app.models import (
    CompiledResult,
    Result,
)

from .models import (
    GradeComplaint,
    JuryDecision,
    JuryMember,
    JurySession,
    OfficialDocument,
    TeacherPaymentClaim,
)

logger = logging.getLogger(__name__)


class AcademicSecretaryService:

    @staticmethod
    def get_dashboard_stats():
        """Get academic secretary dashboard overview statistics"""
        # Upcoming exams (next 30 days)
        upcoming_exams = Exam.objects.filter(
            start_date__gte=timezone.now(),
            start_date__lte=timezone.now() + timedelta(days=30),
        ).count()

        # Pending grade complaints
        pending_complaints = GradeComplaint.objects.filter(
            status__in=["submitted", "assigned", "in_review"]
        ).count()

        # Pending documents (draft or awaiting signature)
        pending_documents = OfficialDocument.objects.filter(
            status__in=["draft", "pending_signature"]
        ).count()

        # Pending payment claims
        pending_claims = TeacherPaymentClaim.objects.filter(
            status__in=["submitted", "verified"]
        ).count()

        # Upcoming jury sessions (next 30 days)
        upcoming_juries = JurySession.objects.filter(
            session_date__gte=timezone.now(),
            session_date__lte=timezone.now() + timedelta(days=30),
            status__in=["scheduled", "in_progress"],
        ).count()

        # Active inscriptions
        active_inscriptions = Inscription.objects.filter(regist_status="Active").count()

        # Pending attributions
        pending_attributions = Attribution.objects.filter(
            status_principal_teacher="Pending"
        ).count()

        return {
            "upcoming_exams": upcoming_exams,
            "pending_complaints": pending_complaints,
            "pending_documents": pending_documents,
            "pending_claims": pending_claims,
            "upcoming_juries": upcoming_juries,
            "active_inscriptions": active_inscriptions,
            "pending_attributions": pending_attributions,
        }

    # ==================== EXAM MANAGEMENT ====================

    @staticmethod
    @transaction.atomic
    def schedule_exam(
        course_id,
        exam_type_id,
        start_date,
        end_date,
        duration_minutes,
        max_marks,
        instructions,
        created_by,
    ):
        """Schedule exam session"""
        exam = Exam.objects.create(
            course_id=course_id,
            exam_type_id=exam_type_id,
            start_date=start_date,
            end_date=end_date,
            duration_minutes=duration_minutes,
            max_marks=max_marks,
            instructions=instructions,
            status="scheduled",
            created_by=created_by,
        )

        return exam

    @staticmethod
    @transaction.atomic
    def assign_exam_room(exam_id, room_id, capacity):
        """Assign room to exam"""
        exam_room = ExamRoom.objects.create(
            exam_id=exam_id, room_id=room_id, capacity=capacity
        )

        return exam_room

    @staticmethod
    @transaction.atomic
    def assign_exam_supervisor(exam_id, supervisor_id):
        """Assign supervisor to exam"""
        # Check for conflicts
        exam = Exam.objects.get(id=exam_id)

        existing_supervision = ExamSupervisor.objects.filter(
            supervisor_id=supervisor_id,
            exam__start_date__lt=exam.end_date,
            exam__end_date__gt=exam.start_date,
        ).exists()

        if existing_supervision:
            raise ValueError("Supervisor has a conflicting exam supervision assignment")

        exam_supervisor = ExamSupervisor.objects.create(
            exam_id=exam_id, supervisor_id=supervisor_id
        )

        return exam_supervisor

    @staticmethod
    def get_exam_list(filters=None):
        """Get list of exams with optional filters"""
        exams = Exam.objects.select_related(
            "course", "exam_type", "created_by"
        ).prefetch_related("exam_rooms__room", "exam_supervisors__supervisor")

        if filters:
            if filters.get("status"):
                exams = exams.filter(status=filters["status"])
            if filters.get("course_id"):
                exams = exams.filter(course_id=filters["course_id"])
            if filters.get("start_date_from"):
                exams = exams.filter(start_date__gte=filters["start_date_from"])
            if filters.get("start_date_to"):
                exams = exams.filter(start_date__lte=filters["start_date_to"])

        return exams.order_by("start_date")

    @staticmethod
    @transaction.atomic
    def update_exam_status(exam_id, status):
        """Update exam status"""
        valid_transitions = {
            "scheduled": ["in_progress", "cancelled"],
            "in_progress": ["completed", "cancelled"],
            "completed": [],
            "cancelled": [],
        }

        exam = Exam.objects.get(id=exam_id)

        if status not in valid_transitions.get(exam.status, []):
            raise ValueError(f"Cannot transition from {exam.status} to {status}")

        exam.status = status
        exam.save()

        return exam

    # ==================== GRADE MONITORING ====================

    @staticmethod
    def check_grade_entry_status(filters=None):
        """Check grade entry completion status by teachers"""
        grade_status = []

        courses = Course.objects.all()

        if filters:
            if filters.get("academic_year_id"):
                courses = courses.filter(
                    attributions__academic_year_id=filters["academic_year_id"]
                )

        for course in courses:
            # Get active attributions for this course
            attribution = (
                Attribution.objects.filter(
                    course=course, status_principal_teacher="Accepted"
                )
                .select_related("principal_teacher__user", "academic_year")
                .first()
            )

            if not attribution:
                continue

            # Count total students enrolled in course
            total_students = Inscription.objects.filter(
                class_fk__courses=course, regist_status="Active"
            ).count()

            # Count grades entered
            grades_entered = Result.objects.filter(
                course=course, mark__isnull=False
            ).count()

            completion_rate = (
                (grades_entered / total_students * 100) if total_students > 0 else 0
            )

            teacher = attribution.principal_teacher
            teacher_name = f"{teacher.user.first_name} {teacher.user.last_name}"

            grade_status.append(
                {
                    "course_id": course.id,
                    "course_name": course.course_name,
                    "course_code": course.course_code,
                    "teacher_id": teacher.id,
                    "teacher_name": teacher_name,
                    "total_students": total_students,
                    "grades_entered": grades_entered,
                    "completion_rate": round(completion_rate, 2),
                    "academic_year": attribution.academic_year.academic_year,
                }
            )

        return grade_status

    @staticmethod
    def get_course_results(course_id, session_id=None):
        """Get results for a specific course"""
        results = Result.objects.filter(course_id=course_id).select_related(
            "inscription__student__user", "course", "session"
        )

        if session_id:
            results = results.filter(session_id=session_id)

        return results.order_by("inscription__student__user__last_name")

    # ==================== JURY MANAGEMENT ====================

    @staticmethod
    @transaction.atomic
    def create_jury_session(session_name, session_date, jury_member_ids, class_group_id, created_by, academic_year_id=None):
        """Create jury session for deliberations with role-based members"""
        from services.core_service.academic_module.class_app.models import ClassGroup
        
        try:
            class_group = ClassGroup.objects.get(id=class_group_id)
        except ClassGroup.DoesNotExist:
            raise ValueError(f"ClassGroup {class_group_id} not found")
        
        jury = JurySession.objects.create(
            session_name=session_name,
            session_date=session_date,
            class_group=class_group,
            status="scheduled",
            created_by=created_by,
        )

        for member_data in jury_member_ids:
            JuryMember.objects.create(
                jury_session=jury,
                user_id=member_data.get("user_id") if isinstance(member_data, dict) else member_data,
                role=member_data.get("role", "member") if isinstance(member_data, dict) else "member",
            )

        # Pre-create JuryDecision entries for all students linked to this class group.
        try:
            from services.core_service.student_module.inscription_app.models import Inscription

            q = Inscription.objects.filter(
                class_group=class_group,
                regist_status__in=["Active", "Pending", "Complement"],
            )
            if academic_year_id:
                q = q.filter(academic_year_id=academic_year_id)

            student_ids = list(q.values_list("student_id", flat=True).distinct())

            # Fallback: if no students found in the exact group, try by class_fk
            if not student_ids:
                logger.info(
                    "No Active/Pending/Complement inscriptions found for "
                    "class_group=%s, trying by class_fk_id=%s",
                    class_group.id, class_group.class_fk_id,
                )
                q2 = Inscription.objects.filter(
                    class_fk_id=class_group.class_fk_id,
                    regist_status__in=["Active", "Pending", "Complement"],
                )
                if academic_year_id:
                    q2 = q2.filter(academic_year_id=academic_year_id)
                student_ids = list(
                    q2.values_list("student_id", flat=True).distinct()
                )

            logger.info(
                "Pre-creating %d JuryDecision(s) for jury_session=%s",
                len(student_ids), jury.id,
            )

            for sid in student_ids:
                try:
                    JuryDecision.objects.get_or_create(
                        jury_session=jury,
                        student_id=sid,
                        defaults={"decision": "ND", "notes": "", "validated_by": None},
                    )
                except Exception as e:
                    logger.exception(
                        "Failed to create JuryDecision for "
                        "jury_session=%s student_id=%s: %s",
                        jury.id, sid, e,
                    )
        except Exception as e:
            logger.exception("JuryDecision pre-creation block failed: %s", e)

        return jury

    @staticmethod
    @transaction.atomic
    def update_jury_status(jury_id, status, minutes_document=None):
        """Update jury session status with president validation"""
        valid_transitions = {
            "scheduled": ["in_progress", "completed"],
            "in_progress": ["completed"],
            "completed": [],
        }

        jury = JurySession.objects.get(id=jury_id)

        if status not in valid_transitions.get(jury.status, []):
            raise ValueError(f"Cannot transition from {jury.status} to {status}")

        if status in ["in_progress", "completed"]:
            has_president = JuryMember.objects.filter(
                jury_session=jury,
                role="president"
            ).exists()
            if not has_president:
                raise ValueError("Cannot transition to this status: session must have a president")

        jury.status = status
        if minutes_document:
            jury.minutes_document = minutes_document
        jury.save()

        return jury

    @staticmethod
    @transaction.atomic
    def record_jury_decision(jury_id, student_id, decision, notes, validated_by):
        """Record jury decision for student"""
        jury = JurySession.objects.get(id=jury_id)

        if jury.status == "completed":
            raise ValueError("Cannot modify decisions for completed jury session")

        jury_decision, created = JuryDecision.objects.update_or_create(
            jury_session_id=jury_id,
            student_id=student_id,
            defaults={
                "decision": decision,
                "notes": notes,
                "validated_by": validated_by,
            },
        )

        # Create notification for student
        from services.core_service.student_module.student_profile_app.models import (
            Student,
        )

        student = Student.objects.get(id=student_id)
        Notification.objects.create(
            recipient=student.user,
            recipient_type="student",
            notification_type="jury_decision",
            title="Jury Decision",
            message=f"A jury decision has been made for you: {decision}",
        )

        # If the decision requires complements (AAC), create a ComplementRequirement
        # so that registrars and finance can follow up.
        if decision == "AAC":
            try:
                from services.core_service.student_module.inscription_app.models import (
                    ComplementRequirement,
                )
                from services.dependent_service.dashboard_module.dashboard_collection_agent_app.models import (
                    FeesSheet,
                )

                # try to find the relevant inscription for this student in the same class group
                inscription = (
                    Inscription.objects.filter(
                        student=student, class_group=jury.class_group
                    )
                    .order_by("-academic_year_id")
                    .first()
                )

                feesheet = None
                unit_price = 0
                if jury.class_group and hasattr(jury.class_group, "academic_year"):
                    feesheet = (
                        FeesSheet.objects.filter(
                            wording__wording_name__icontains="compl",
                            academic_year=jury.class_group.academic_year,
                            class_fk=jury.class_group.class_fk,
                        )
                        .order_by("-base_amount")
                        .first()
                    )
                    if not feesheet:
                        feesheet = (
                            FeesSheet.objects.filter(
                                wording__wording_name__icontains="compl",
                                academic_year=jury.class_group.academic_year,
                            )
                            .order_by("-base_amount")
                            .first()
                        )
                if feesheet:
                    unit_price = feesheet.base_amount

                ComplementRequirement.objects.create(
                    student=student,
                    inscription=inscription,
                    requirements="Compléments à définir",
                    course_count=1,
                    unit_price=unit_price,
                    feesheet=feesheet,
                    status="pending",
                    created_by=validated_by,
                )

                # mark the inscription as 'Complement' so it appears in registries
                if inscription:
                    Inscription.objects.filter(pk=inscription.pk).update(regist_status="Complement")

                Notification.objects.create(
                    recipient=student.user,
                    recipient_type="student",
                    notification_type="academic",
                    title="Complément requis",
                    message=(
                        "Votre dossier nécessite des compléments suite à la décision 'Avance avec complément'. "
                        "Veuillez consulter le bureau des inscriptions pour les détails."
                    ),
                )
            except Exception:
                # don't break the decision recording if complement creation fails
                pass

        return jury_decision

    @staticmethod
    def get_jury_sessions(filters=None):
        """Get jury sessions with optional filters"""
        sessions = JurySession.objects.select_related("created_by").prefetch_related(
            "jury_member_records__user"
        )

        if filters:
            if filters.get("status"):
                sessions = sessions.filter(status=filters["status"])
            if filters.get("date_from"):
                sessions = sessions.filter(session_date__gte=filters["date_from"])
            if filters.get("date_to"):
                sessions = sessions.filter(session_date__lte=filters["date_to"])

        return sessions.order_by("-session_date")

    @staticmethod
    def get_jury_decisions(jury_id):
        """Get all decisions for a jury session"""
        decisions = JuryDecision.objects.filter(jury_session_id=jury_id).select_related(
            "student__user", "validated_by"
        )

        return decisions

    # ==================== GRADE COMPLAINT MANAGEMENT ====================

    @staticmethod
    @transaction.atomic
    def assign_grade_complaint(complaint_id, assigned_to_id):
        """Assign grade complaint to teacher or department head"""
        complaint = GradeComplaint.objects.get(id=complaint_id)

        if complaint.status not in ["submitted"]:
            raise ValueError("Can only assign complaints with 'submitted' status")

        complaint.assigned_to_id = assigned_to_id
        complaint.status = "assigned"
        complaint.save()

        # Notify assigned person
        Notification.objects.create(
            recipient_id=assigned_to_id,
            recipient_type="staff",
            notification_type="complaint_assigned",
            title="Grade Complaint Assigned",
            message=f"A grade complaint for {complaint.course.course_name} has been assigned to you",
        )

        return complaint

    @staticmethod
    @transaction.atomic
    def update_complaint_status(complaint_id, status):
        """Update complaint status"""
        valid_transitions = {
            "submitted": ["assigned", "rejected"],
            "assigned": ["in_review", "rejected"],
            "in_review": ["resolved", "rejected"],
            "resolved": [],
            "rejected": [],
        }

        complaint = GradeComplaint.objects.get(id=complaint_id)

        if status not in valid_transitions.get(complaint.status, []):
            raise ValueError(f"Cannot transition from {complaint.status} to {status}")

        complaint.status = status
        complaint.save()

        return complaint

    @staticmethod
    @transaction.atomic
    def resolve_grade_complaint(complaint_id, new_grade, resolution_notes, resolved_by):
        """Resolve grade complaint with new grade"""
        complaint = GradeComplaint.objects.get(id=complaint_id)

        if complaint.status not in ["in_review"]:
            raise ValueError("Can only resolve complaints with 'in_review' status")

        complaint.new_grade = new_grade
        complaint.resolution_notes = resolution_notes
        complaint.status = "resolved"
        complaint.resolved_at = timezone.now()
        complaint.save()

        # Update the actual grade in the system if new grade is different
        if new_grade is not None and new_grade != complaint.original_grade:
            Result.objects.filter(
                course=complaint.course, inscription__student=complaint.student
            ).update(mark=new_grade)

        # Notify student
        Notification.objects.create(
            recipient=complaint.student.user,
            recipient_type="student",
            notification_type="complaint_resolved",
            title="Grade Complaint Resolved",
            message=f"Your complaint for {complaint.course.course_name} has been resolved",
        )

        return complaint

    @staticmethod
    def get_grade_complaints(filters=None):
        """Get grade complaints with optional filters"""
        complaints = GradeComplaint.objects.select_related(
            "student__user", "course", "assigned_to"
        )

        if filters:
            if filters.get("status"):
                complaints = complaints.filter(status=filters["status"])
            if filters.get("course_id"):
                complaints = complaints.filter(course_id=filters["course_id"])
            if filters.get("student_id"):
                complaints = complaints.filter(student_id=filters["student_id"])

        return complaints.order_by("-submitted_at")

    # ==================== OFFICIAL DOCUMENT MANAGEMENT ====================

    @staticmethod
    @transaction.atomic
    def create_official_document(doc_type, title, content, created_by):
        """Create official document (circular, service note, etc.)"""
        document = OfficialDocument.objects.create(
            document_type=doc_type,
            title=title,
            content=content,
            status="draft",
            created_by=created_by,
        )

        return document

    @staticmethod
    @transaction.atomic
    def update_document_status(document_id, status):
        """Update document status"""
        valid_transitions = {
            "draft": ["pending_signature", "archived"],
            "pending_signature": ["signed", "draft"],
            "signed": ["archived"],
            "archived": [],
        }

        document = OfficialDocument.objects.get(id=document_id)

        if status not in valid_transitions.get(document.status, []):
            raise ValueError(f"Cannot transition from {document.status} to {status}")

        document.status = status
        document.save()

        return document

    @staticmethod
    @transaction.atomic
    def sign_document(document_id, signed_by):
        """Sign official document"""
        document = OfficialDocument.objects.get(id=document_id)

        if document.status != "pending_signature":
            raise ValueError("Document must be in 'pending_signature' status to sign")

        document.signed_by = signed_by
        document.signed_at = timezone.now()
        document.status = "signed"
        document.save()

        return document

    @staticmethod
    def get_official_documents(filters=None):
        """Get official documents with optional filters"""
        documents = OfficialDocument.objects.select_related("created_by", "signed_by")

        if filters:
            if filters.get("document_type"):
                documents = documents.filter(document_type=filters["document_type"])
            if filters.get("status"):
                documents = documents.filter(status=filters["status"])

        return documents.order_by("-created_at")

    # ==================== TEACHER PAYMENT CLAIM MANAGEMENT ====================

    @staticmethod
    @transaction.atomic
    def verify_payment_claim(claim_id, verified_by):
        """Verify teacher payment claim"""
        claim = TeacherPaymentClaim.objects.get(id=claim_id)

        if claim.status != "submitted":
            raise ValueError("Can only verify claims with 'submitted' status")

        # Verify calculation
        expected_total = claim.hours_taught * claim.hourly_rate
        if abs(float(claim.total_amount) - float(expected_total)) > 0.01:
            raise ValueError("Claim total amount does not match calculation")

        claim.verified_by = verified_by
        claim.status = "verified"
        claim.save()

        # Notify teacher
        Notification.objects.create(
            recipient=claim.teacher.user,
            recipient_type="teacher",
            notification_type="claim_verified",
            title="Payment Claim Verified",
            message=f"Your payment claim for {claim.course.course_name} has been verified",
        )

        return claim

    @staticmethod
    @transaction.atomic
    def approve_payment_claim(claim_id, approved_by):
        """Approve verified payment claim"""
        claim = TeacherPaymentClaim.objects.get(id=claim_id)

        if claim.status != "verified":
            raise ValueError("Can only approve claims with 'verified' status")

        claim.approved_by = approved_by
        claim.status = "approved"
        claim.processed_at = timezone.now()
        claim.save()

        return claim

    @staticmethod
    @transaction.atomic
    def sign_payment_claim(claim_id, signed_by):
        """Sign approved payment claim"""
        claim = TeacherPaymentClaim.objects.get(id=claim_id)

        if claim.status != "approved":
            raise ValueError("Can only sign claims with 'approved' status")

        claim.status = "signed"
        claim.save()

        return claim

    @staticmethod
    @transaction.atomic
    def send_claim_to_finance(claim_id):
        """Send signed claim to financial service"""
        claim = TeacherPaymentClaim.objects.get(id=claim_id)

        if claim.status != "signed":
            raise ValueError("Can only send claims with 'signed' status to finance")

        claim.status = "sent_to_finance"
        claim.save()

        return claim

    @staticmethod
    @transaction.atomic
    def reject_payment_claim(claim_id, rejection_reason):
        """Reject payment claim"""
        claim = TeacherPaymentClaim.objects.get(id=claim_id)

        if claim.status in ["sent_to_finance"]:
            raise ValueError("Cannot reject claims already sent to finance")

        claim.status = "rejected"
        claim.save()

        # Notify teacher
        Notification.objects.create(
            recipient=claim.teacher.user,
            recipient_type="teacher",
            notification_type="claim_rejected",
            title="Payment Claim Rejected",
            message=f"Your payment claim for {claim.course.course_name} has been rejected: {rejection_reason}",
        )

        return claim

    @staticmethod
    def get_payment_claims(filters=None):
        """Get teacher payment claims with optional filters"""
        claims = TeacherPaymentClaim.objects.select_related(
            "teacher__user", "course", "verified_by", "approved_by"
        )

        if filters:
            if filters.get("status"):
                claims = claims.filter(status=filters["status"])
            if filters.get("teacher_id"):
                claims = claims.filter(teacher_id=filters["teacher_id"])
            if filters.get("course_id"):
                claims = claims.filter(course_id=filters["course_id"])

        return claims.order_by("-submitted_at")

    # ==================== INSCRIPTION MANAGEMENT ====================

    @staticmethod
    def get_inscriptions(filters=None):
        """Get student inscriptions with optional filters"""
        inscriptions = Inscription.objects.select_related(
            "student__user", "class_fk", "academic_year"
        )

        if filters:
            if filters.get("status"):
                inscriptions = inscriptions.filter(regist_status=filters["status"])
            if filters.get("academic_year_id"):
                inscriptions = inscriptions.filter(
                    academic_year_id=filters["academic_year_id"]
                )
            if filters.get("class_id"):
                inscriptions = inscriptions.filter(class_fk_id=filters["class_id"])

        return inscriptions.order_by("-registration_date")

    @staticmethod
    def get_inscription_statistics(academic_year_id=None):
        """Get inscription statistics"""
        inscriptions = Inscription.objects.all()

        if academic_year_id:
            inscriptions = inscriptions.filter(academic_year_id=academic_year_id)

        total = inscriptions.count()
        active = inscriptions.filter(regist_status="Active").count()
        pending = inscriptions.filter(regist_status="Pending").count()
        cancelled = inscriptions.filter(regist_status="Cancelled").count()

        # By class
        by_class = (
            inscriptions.values("class_fk__class_name")
            .annotate(count=Count("id"))
            .order_by("-count")
        )

        return {
            "total": total,
            "active": active,
            "pending": pending,
            "cancelled": cancelled,
            "by_class": list(by_class),
        }

    # ==================== RESULT COMPILATION ====================

    @staticmethod
    def get_compilation_status(academic_year_id=None):
        """Get result compilation status"""
        inscriptions = Inscription.objects.filter(regist_status="Active")

        if academic_year_id:
            inscriptions = inscriptions.filter(academic_year_id=academic_year_id)

        total_students = inscriptions.count()
        compiled = CompiledResult.objects.filter(inscription__in=inscriptions).count()

        completion_rate = (compiled / total_students * 100) if total_students > 0 else 0

        # Status breakdown
        status_breakdown = (
            CompiledResult.objects.filter(inscription__in=inscriptions)
            .values("status")
            .annotate(count=Count("id"))
        )

        return {
            "total_students": total_students,
            "compiled_results": compiled,
            "completion_rate": round(completion_rate, 2),
            "status_breakdown": list(status_breakdown),
        }
