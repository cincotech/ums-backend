from django.db.models import Avg, Sum
from django.utils import timezone

from services.core_service.student_module.inscription_app.models import Inscription
from services.dependent_service.dashboard_module.dashboard_collection_agent_app.models import (
    FeesSheet,
    Payment,
)
from services.dependent_service.dashboard_module.dashboard_shared_app.models import (
    Message,
    Notification,
)
from services.dependent_service.document_module.request_app.models import Request
from services.dependent_service.exam_module.result_app.models import (
    CompiledResult,
    Result,
)
from services.dependent_service.scheduling_module.scheduling_app.models import (
    Attendance,
)
from services.dependent_service.dashboard_module.dashboard_doyen_app.services import ClassGroupManagementService


class StudentDashboardService:

    @staticmethod
    def get_student_dashboard_stats(student):
        """Get student dashboard overview statistics"""
        unread_notifications = Notification.objects.filter(
            recipient=student.user, is_read=False
        ).count()

        pending_documents = Request.objects.filter(
            student=student, request_status__in=["pending", "processing"]
        ).count()

        # Calculate GPA from results
        results = Result.objects.filter(inscription__student=student)
        current_gpa = results.aggregate(avg=Avg("mark"))["avg"] or 0.0

        # Calculate attendance rate
        total_attendance = Attendance.objects.filter(
            student=student
        ).count()
        present_count = Attendance.objects.filter(
            student=student, status__in=["present", "justified"]
        ).count()
        attendance_rate = (
            (present_count / total_attendance * 100) if total_attendance > 0 else 0
        )

        # Check payment status
        payment_status = (
            "paid"
            if StudentDashboardService._check_payment_status(student)
            else "pending"
        )

        # Credits earned (simplified)
        credits_earned = (
            CompiledResult.objects.filter(
                inscription__student=student, status="passed"
            ).count()
            * 30
        )  # Assuming 30 credits per semester

        return {
            "unread_notifications": unread_notifications,
            "pending_documents": pending_documents,
            "current_gpa": round(current_gpa, 2),
            "attendance_rate": round(attendance_rate, 2),
            "payment_status": payment_status,
            "credits_earned": credits_earned,
        }

    @staticmethod
    def get_student_profile(student):
        """Get student profile information"""
        inscription = Inscription.objects.filter(
            student=student, regist_status="Active"
        ).first()
        program = student.graduate_infos.first()

        return {
            "student_id": student.id,
            "matricule": student.matricule,
            "full_name": f"{student.user.first_name} {student.user.last_name}",
            "email": student.user.email,
            "phone_number": student.user.phone_number or "",
            "program": program.department.name if program else "N/A",
            "academic_year": str(inscription.academic_year) if inscription else "N/A",
            "payment_status": StudentDashboardService._get_payment_status(student),
        }

    @staticmethod
    def get_student_grades(student, payment_required=True):
        """Get student grades (conditional on payment)"""
        if payment_required and not StudentDashboardService._check_payment_status(
            student
        ):
            return {"error": "Payment required to access grades"}

        results = Result.objects.filter(inscription__student=student).select_related(
            "course"
        )

        return results

    @staticmethod
    def get_student_transcript(student, academic_year_id=None):
        """Get official transcript (only when academic year is closed)

        Args:
            student: Student object
            academic_year_id: Optional UUID of specific academic year

        Returns:
            QuerySet of CompiledResult or dict with error
        """
        from services.core_service.academic_module.university_app.models import (
            AcademicYear,
        )

        if academic_year_id:
            # Check specific year
            try:
                academic_year = AcademicYear.objects.get(id=academic_year_id)
                if not academic_year.is_closed:
                    return {
                        "error": f"Transcript for {academic_year.academic_year} is not available yet. Academic year must be closed first."
                    }

                compiled_results = CompiledResult.objects.filter(
                    inscription__student=student,
                    inscription__academic_year=academic_year,
                ).select_related(
                    "inscription", "inscription__academic_year", "inscription__class_fk"
                )

            except AcademicYear.DoesNotExist:
                return {"error": "Academic year not found"}
        else:
            # Get all transcripts for closed years only
            closed_years = AcademicYear.objects.filter(is_closed=True)
            compiled_results = (
                CompiledResult.objects.filter(
                    inscription__student=student,
                    inscription__academic_year__in=closed_years,
                )
                .order_by("-inscription__academic_year__start_date")
                .select_related(
                    "inscription", "inscription__academic_year", "inscription__class_fk"
                )
            )

        return compiled_results

    @staticmethod
    def get_academic_progress(student):
        """Get student academic progression and credits"""
        program = student.graduate_infos.first()
        if not program:
            return {"error": "No program information found"}

        # Simplified credit calculation
        total_credits_required = 180  # Bachelor's degree
        if program.degree.name.lower() in ["master", "masters"]:
            total_credits_required = 120

        credits_earned = (
            CompiledResult.objects.filter(
                inscription__student=student, status="passed"
            ).count()
            * 30
        )

        credits_remaining = max(0, total_credits_required - credits_earned)
        completion_percentage = (
            (credits_earned / total_credits_required * 100)
            if total_credits_required > 0
            else 0
        )

        # Current GPA
        gpa = (
            Result.objects.filter(inscription__student=student).aggregate(
                avg=Avg("mark")
            )["avg"]
            or 0.0
        )

        return {
            "total_credits_required": total_credits_required,
            "credits_earned": credits_earned,
            "credits_remaining": credits_remaining,
            "current_semester": "Current",  # Would need proper semester tracking
            "gpa": round(gpa, 2),
            "completion_percentage": round(completion_percentage, 2),
        }

    @staticmethod
    def get_student_schedule(student):
        """Get the student's class schedule based on their active inscription."""
        from services.dependent_service.scheduling_module.scheduling_app.models import Timetable

        # Get the student's active inscription
        inscription = (
            Inscription.objects.filter(student=student, regist_status="Active")
            .select_related('class_fk', 'academic_year') 
            .first()
        )

        if not inscription :
            return Timetable.objects.none()
      

        # If no group assigned, assign default G1 automatically
        if not inscription.class_group:
            default_group = ClassGroupManagementService.get_or_create_default_group(
                class_fk=inscription.class_fk,
                academic_year=inscription.academic_year
            )
            inscription.class_group = default_group
            inscription.save(update_fields=['class_group'])

        class_group = inscription.class_group

        # Only use the assigned class_group
        class_group = inscription.class_group

        # Return timetable entries for this class group
        return Timetable.objects.filter(class_group=class_group) .select_related(
                'class_group',
                'attribution',
                'attribution__course',
                'attribution__principal_teacher',
                'room'
            ).prefetch_related('slots').order_by('start_date')[1:2]


    @staticmethod
    def get_student_attendance(student):
        """Get student attendance record"""
        return Attendance.objects.filter(student=student)

    @staticmethod
    def send_message(student, recipient_id, subject, content, message_type):
        """Send message to teacher or administration"""
        from services.foundational_service.auth_module.user_app.models import User

        recipient = User.objects.get(id=recipient_id)

        message = Message.objects.create(
            message_type=message_type,
            recipient=recipient,
            sender=student.user,
            subject=subject,
            content=content,
        )

        return message

    @staticmethod
    def request_document(student, document_id, request_date, payment=None):
        """Request official document"""

        from services.dependent_service.document_module.document_app.models import (
            Document,
        )

        document = Document.objects.get(id=document_id)

        document_request = Request.objects.create(
            student=student,
            document=document,
            request_date=request_date or timezone.now(),
            request_status="pending",
            payment=payment,
        )

        # Create notification for student services
        Notification.objects.create(
            recipient=student.user,
            recipient_type="student",
            notification_type="document_ready",
            title="Document Request Submitted",
            message=f"Your request for {document.name} has been submitted and is being processed.",
        )

        return document_request

    @staticmethod
    def update_profile(student, profile_data):
        """Update student profile information"""
        user = student.user

        # Update user fields
        for field in ["first_name", "last_name", "email", "phone_number"]:
            if field in profile_data:
                setattr(user, field, profile_data[field])

        user.save()

        # Update student fields if any
        for field in ["matricule"]:
            if field in profile_data:
                setattr(student, field, profile_data[field])

        student.save()

        return student

    @staticmethod
    def mark_notification_read(notification_id, student):
        """Mark notification as read"""
        notification = Notification.objects.get(
            id=notification_id, recipient=student.user
        )

        notification.is_read = True
        notification.save()

        return notification

    @staticmethod
    def _check_payment_status(student):
        """Check if student has paid required installment for current academic year

        Returns True if:
        - Student has an active inscription
        - Student has paid at least the minimum required installment
        - Payment is verified
        """
        from django.utils import timezone

        # Get active inscription
        active_inscription = (
            Inscription.objects.filter(student=student, regist_status="ACT")
            .order_by("-academic_year__start_date")
            .first()
        )

        if not active_inscription:
            return False

        # Get fees sheet for current inscription
        try:
            fees_sheet = FeesSheet.objects.get(
                class_fk=active_inscription.class_fk,
                academic_year=active_inscription.academic_year,
            )
        except FeesSheet.DoesNotExist:
            # If no fees sheet exists, allow access
            return True

        # Get installments configuration
        installments = fees_sheet.installements or []
        if not installments:
            # If no installments configured, check if total is paid
            total_paid = (
                Payment.objects.filter(
                    inscription=active_inscription, payment_status="verified"
                ).aggregate(total=Sum("amount_paid"))["total"]
                or 0
            )

            return total_paid >= fees_sheet.base_amount

        # Check which installment should be paid by now
        today = timezone.now().date()
        required_amount = 0

        for installment in installments:
            # installment format: {"deadline": "YYYY-MM-DD", "amount": 12345, "name": "1st Installment"}
            deadline = installment.get("deadline")
            if deadline:
                from datetime import datetime

                deadline_date = datetime.fromisoformat(str(deadline)).date()
                if deadline_date <= today:
                    required_amount += installment.get("amount", 0)

        # Get total verified payments for this inscription
        total_paid = (
            Payment.objects.filter(
                inscription=active_inscription, payment_status="verified"
            ).aggregate(total=Sum("amount_paid"))["total"]
            or 0
        )

        return total_paid >= required_amount

    @staticmethod
    def _get_payment_status(student):
        """Get student payment status"""
        if StudentDashboardService._check_payment_status(student):
            return "paid"
        return "pending"

    @staticmethod
    def get_student_jury_decisions(student):
        """Get jury decisions for student"""
        from services.dependent_service.dashboard_module.dashboard_academic_secretary_app.models import (
            JuryDecision,
        )

        decisions = JuryDecision.objects.filter(student=student).select_related(
            "jury_session", "validated_by"
        )

        return decisions

    @staticmethod
    def get_student_grade_complaints(student):
        """Get grade complaints submitted by student"""
        from services.dependent_service.dashboard_module.dashboard_academic_secretary_app.models import (
            GradeComplaint,
        )

        complaints = GradeComplaint.objects.filter(student=student).select_related(
            "course", "assigned_to"
        )

        return complaints

    @staticmethod
    def submit_grade_complaint(student, course_id, original_grade, complaint_reason):
        """Submit grade complaint for a course"""
        from services.core_service.academic_module.course_app.models import Course
        from services.dependent_service.dashboard_module.dashboard_academic_secretary_app.models import (
            GradeComplaint,
        )

        course = Course.objects.get(id=course_id)

        # Verify student has this course and grade
        result = Result.objects.filter(
            inscription__student=student, course=course
        ).first()

        if not result:
            raise ValueError("You don't have a grade for this course")

        # Check if complaint already exists
        existing_complaint = GradeComplaint.objects.filter(
            student=student,
            course=course,
            status__in=["submitted", "assigned", "in_review"],
        ).exists()

        if existing_complaint:
            raise ValueError("A complaint for this course is already pending")

        complaint = GradeComplaint.objects.create(
            student=student,
            course=course,
            original_grade=original_grade,
            complaint_reason=complaint_reason,
            status="submitted",
        )

        # Create notification for academic secretary
        Notification.objects.create(
            recipient=student.user,
            recipient_type="student",
            notification_type="complaint_submitted",
            title="Grade Complaint Submitted",
            message=f"Your grade complaint for {course.course_name} has been submitted and will be reviewed.",
        )

        return complaint

    @staticmethod
    def get_student_exams(student):
        """Get upcoming exams for student"""
        from services.dependent_service.exam_module.exam_app.models import Exam

        # Get student's active inscription
        inscription = Inscription.objects.filter(
            student=student, regist_status="Active"
        ).first()

        if not inscription:
            return []

        # Get exams for courses in student's class
        exams = (
            Exam.objects.filter(course__classes=inscription.class_fk)
            .select_related("course", "exam_type", "created_by")
            .order_by("start_date")
        )

        return exams

    @staticmethod
    def get_official_documents(student):
        """Get official documents relevant to student (circulars, service notes)"""
        from services.dependent_service.dashboard_module.dashboard_academic_secretary_app.models import (
            OfficialDocument,
        )

        # Get signed documents (circulars and service notes only)
        documents = OfficialDocument.objects.filter(
            document_type__in=["circular", "service_note"], status="signed"
        ).select_related("created_by", "signed_by")

        return documents

    @staticmethod
    def get_student_payments(student):
        """Get student payment history"""
        # Get student's active inscription
        inscription = Inscription.objects.filter(
            student=student, regist_status="Active"
        ).first()

        if not inscription:
            return []

        payments = Payment.objects.filter(inscription=inscription).order_by(
            "-payment_date"
        )

        return payments

    @staticmethod
    def get_student_messages(student):
        """Get student messages"""
        messages = Message.objects.filter(recipient=student.user).order_by("-sent_at")
        return messages

    @staticmethod
    def get_student_notifications(student):
        """Get student notifications"""
        notifications = Notification.objects.filter(recipient=student.user).order_by(
            "-created_at"
        )
        return notifications

    @staticmethod
    def get_document_requests(student):
        """Get student document requests"""
        requests = Request.objects.filter(student=student).select_related("document")
        return requests

    @staticmethod
    def get_downloadable_document(student, document_type):
        """Get downloadable document (transcript, etc.)"""
        # Check payment status for certain documents
        if document_type in ["transcript", "certificate"]:
            if not StudentDashboardService._check_payment_status(student):
                return {
                    "error": True,
                    "message": "Payment required to access this document",
                }

        # Return document data (simplified)
        return {"document_type": document_type, "available": True}
