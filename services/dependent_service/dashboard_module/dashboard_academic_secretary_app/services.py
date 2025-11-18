from datetime import timedelta

from django.utils import timezone

from services.core_service.academic_module.course_app.models import Course
from services.dependent_service.exam_module.attendance_app.models import ExamAttendance
from services.dependent_service.exam_module.exam_app.models import Exam
from services.dependent_service.exam_module.result_app.models import Result

from .models import (
    GradeComplaint,
    JuryDecision,
    JurySession,
    OfficialDocument,
    TeacherPaymentClaim,
)


class AcademicSecretaryService:

    @staticmethod
    def get_dashboard_stats():
        """Get academic secretary dashboard overview"""
        pending_exams = Exam.objects.filter(exam_date__gte=timezone.now()).count()

        pending_complaints = GradeComplaint.objects.filter(
            status__in=["submitted", "assigned", "in_review"]
        ).count()

        pending_documents = OfficialDocument.objects.filter(
            status__in=["draft", "pending_signature"]
        ).count()

        pending_claims = TeacherPaymentClaim.objects.filter(
            status__in=["submitted", "verified"]
        ).count()

        upcoming_juries = JurySession.objects.filter(
            session_date__gte=timezone.now(),
            session_date__lte=timezone.now() + timedelta(days=30),
            status="scheduled",
        ).count()

        return {
            "pending_exams": pending_exams,
            "pending_complaints": pending_complaints,
            "pending_documents": pending_documents,
            "pending_claims": pending_claims,
            "upcoming_juries": upcoming_juries,
        }

    @staticmethod
    def schedule_exam(course_id, exam_date, duration, room, supervisor_ids, user):
        """Schedule exam session"""
        exam = Exam.objects.create(
            course_id=course_id,
            exam_date=exam_date,
            duration_minutes=duration,
            room=room,
            created_by=user,
        )

        exam.supervisors.set(supervisor_ids)
        return exam

    @staticmethod
    def record_exam_attendance(exam_id, student_id, status, incident_notes, user):
        """Record student exam attendance"""
        attendance, created = ExamAttendance.objects.get_or_create(
            exam_session_id=exam_id,
            student_id=student_id,
            defaults={
                "status": status,
                "incident_notes": incident_notes,
                "recorded_by": user,
            },
        )

        if not created:
            attendance.status = status
            attendance.incident_notes = incident_notes
            attendance.save()

        return attendance

    @staticmethod
    def check_grade_entry_status():
        """Check grade entry completion status by teachers"""
        grade_status = []

        for course in Course.objects.all():
            # Count total students enrolled in course
            total_students = (
                Result.objects.filter(course=course)
                .values("inscription__student")
                .distinct()
                .count()
            )

            # Count grades entered
            grades_entered = Result.objects.filter(
                course=course, mark__isnull=False
            ).count()

            completion_rate = (
                (grades_entered / total_students * 100) if total_students > 0 else 0
            )

            # Get teacher info
            attribution = course.attributions.first()
            teacher_name = "Unknown"
            if attribution and attribution.principal_teacher:
                teacher = attribution.principal_teacher
                teacher_name = f"{teacher.user.first_name} {teacher.user.last_name}"

            grade_status.append(
                {
                    "course_id": course.id,
                    "course_name": course.course_name,
                    "teacher_name": teacher_name,
                    "total_students": total_students,
                    "grades_entered": grades_entered,
                    "completion_rate": round(completion_rate, 2),
                    "deadline": timezone.now() + timedelta(days=7),  # Example deadline
                }
            )

        return grade_status

    @staticmethod
    def create_jury_session(session_name, session_date, jury_member_ids, user):
        """Create jury session for deliberations"""
        jury = JurySession.objects.create(
            session_name=session_name, session_date=session_date, created_by=user
        )

        jury.jury_members.set(jury_member_ids)
        return jury

    @staticmethod
    def record_jury_decision(jury_id, student_id, decision, notes, user):
        """Record jury decision for student"""
        jury_decision = JuryDecision.objects.create(
            jury_session_id=jury_id,
            student_id=student_id,
            decision=decision,
            notes=notes,
            validated_by=user,
        )

        return jury_decision

    @staticmethod
    def assign_grade_complaint(complaint_id, assigned_to_id, user):
        """Assign grade complaint to teacher or department head"""
        complaint = GradeComplaint.objects.get(id=complaint_id)
        complaint.assigned_to_id = assigned_to_id
        complaint.status = "assigned"
        complaint.save()

        return complaint

    @staticmethod
    def resolve_grade_complaint(complaint_id, new_grade, resolution_notes, user):
        """Resolve grade complaint with new grade"""
        complaint = GradeComplaint.objects.get(id=complaint_id)
        complaint.new_grade = new_grade
        complaint.resolution_notes = resolution_notes
        complaint.status = "resolved"
        complaint.resolved_at = timezone.now()
        complaint.save()

        # Update the actual grade in the system
        if new_grade is not None:
            Result.objects.filter(
                course=complaint.course, inscription__student=complaint.student
            ).update(mark=new_grade)

        return complaint

    @staticmethod
    def create_official_document(doc_type, title, content, user):
        """Create official document (circular, service note, etc.)"""
        document = OfficialDocument.objects.create(
            document_type=doc_type, title=title, content=content, created_by=user
        )

        return document

    @staticmethod
    def sign_document(document_id, user):
        """Sign official document"""
        document = OfficialDocument.objects.get(id=document_id)
        document.signed_by = user
        document.signed_at = timezone.now()
        document.status = "signed"
        document.save()

        return document

    @staticmethod
    def verify_payment_claim(claim_id, user):
        """Verify teacher payment claim"""
        claim = TeacherPaymentClaim.objects.get(id=claim_id)

        # Verify hourly rate compliance (simplified)
        # In real implementation, check against configured rates

        claim.verified_by = user
        claim.status = "verified"
        claim.save()

        return claim

    @staticmethod
    def approve_payment_claim(claim_id, user):
        """Approve verified payment claim"""
        claim = TeacherPaymentClaim.objects.get(id=claim_id)
        claim.approved_by = user
        claim.status = "approved"
        claim.processed_at = timezone.now()
        claim.save()

        return claim

    @staticmethod
    def send_claim_to_finance(claim_id, user):
        """Send approved claim to financial service"""
        claim = TeacherPaymentClaim.objects.get(id=claim_id)
        claim.status = "sent_to_finance"
        claim.save()

        # In real implementation, this would integrate with financial system

        return claim

    @staticmethod
    def generate_exam_convocations(exam_id):
        """Generate individual exam convocations for students"""
        Exam.objects.get(id=exam_id)

        # Get enrolled students for the course
        # This would generate individual convocation documents
        convocations = []

        # Simplified implementation
        # In real system, this would generate PDF documents

        return convocations

    @staticmethod
    def archive_document(document_id, user):
        """Archive signed document securely"""
        document = OfficialDocument.objects.get(id=document_id)
        document.status = "archived"
        document.save()

        # In real implementation, this would move to secure archive storage

        return document
