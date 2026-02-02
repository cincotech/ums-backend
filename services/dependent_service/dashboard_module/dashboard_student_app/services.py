from django.db.models import Avg, Sum
from django.utils import timezone

from services.core_service.student_module.inscription_app.models import Inscription
from services.dependent_service.dashboard_module.dashboard_collection_agent_app.models import (
    FeesSheet,
    Payment,
    PaymentPlan,
    PaymentInstallement,
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

        # Get payment information
        payment_info = StudentDashboardService._get_payment_info(student)
        
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
            "amount_paid": payment_info["amount_paid"],
            "total_amount": payment_info["total_amount"],
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
        """Get student class schedule including merged timetables"""
        from services.dependent_service.scheduling_module.scheduling_app.models import Timetable, TimetableMerge
        from django.db.models import Q

        inscription = Inscription.objects.filter(
            student=student, regist_status="Active"
        ).select_related('class_fk', 'academic_year').first()

        if not inscription:
            return {
                'timetables': Timetable.objects.none(),
                'merged_timetables': TimetableMerge.objects.none()
            }

        if not inscription.class_group:
            default_group = ClassGroupManagementService.get_or_create_default_group(
                class_fk=inscription.class_fk,
                academic_year=inscription.academic_year
            )
            inscription.class_group = default_group
            inscription.save(update_fields=['class_group'])

        # Get regular timetables (primary + shared)
        timetables = Timetable.objects.filter(
            Q(class_group=inscription.class_group) | Q(shared_with=inscription.class_group)
        ).select_related(
            'class_group',
            'attribution',
            'attribution__course',
            'attribution__principal_teacher',
            'room'
        ).prefetch_related('slots', 'shared_with').distinct()
        
        # Get merged timetables (check both primary and shared)
        merged_timetables = TimetableMerge.objects.filter(
            Q(timetables__class_group=inscription.class_group) | 
            Q(timetables__shared_with=inscription.class_group)
        ).prefetch_related('timetables', 'timetables__slots').distinct()
        
        return {
            'timetables': timetables.order_by('start_date'),
            'merged_timetables': merged_timetables
        }


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
    def _get_fees_sheets_for_inscription(inscription):
        """Get applicable fees sheets for inscription (class -> department -> faculty)"""
        from django.db.models import Q
        
        fees_sheets = FeesSheet.objects.filter(
            Q(class_fk=inscription.class_fk, academic_year=inscription.academic_year) |
            Q(department=inscription.class_fk.department, academic_year=inscription.academic_year) |
            Q(faculty=inscription.class_fk.department.faculty, academic_year=inscription.academic_year)
        ).order_by('class_fk', 'department', 'faculty') 
        
        return fees_sheets

    @staticmethod
    def _check_payment_status(student):
        """Check if student has paid required installment using PaymentPlan and PaymentInstallement

        Returns True if:
        - Student has an active inscription
        - Student has a payment plan with current installments paid
        - Payment is verified
        """
        from django.utils import timezone

        # Get active inscription
        active_inscription = (
            Inscription.objects.filter(student=student, regist_status="Active")
            .order_by("-academic_year__start_date")
            .first()
        )

        if not active_inscription:
            return False

        # Get fees sheets for current inscription
        fees_sheets = StudentDashboardService._get_fees_sheets_for_inscription(active_inscription)
        
        if not fees_sheets.exists():
            return True

        # Check payment status for all applicable fees sheets
        today = timezone.now().date()
        
        for fees_sheet in fees_sheets:
            # Get payment plans for this fees sheet
            payment_plans = PaymentPlan.objects.filter(feessheet=fees_sheet)
            
            if payment_plans.exists():
                # Check installments for each payment plan
                for payment_plan in payment_plans:
                    due_installments = PaymentInstallement.objects.filter(
                        payment_plan=payment_plan,
                        student=student,
                        due_date__lte=today
                    )
                    
                    required_amount = due_installments.aggregate(
                        total=Sum("amount")
                    )["total"] or 0
                    
                    if required_amount > 0:
                        # Get total verified payments for this inscription
                        total_paid = (
                            Payment.objects.filter(
                                inscription=active_inscription, 
                                payment_status="verified",
                                paymentplan=payment_plan
                            ).aggregate(total=Sum("amount_paid"))["total"]
                            or 0
                        )
                        
                        if total_paid < required_amount:
                            return False
            else:
                # No payment plan, check direct payments against fees sheet
                total_paid = (
                    Payment.objects.filter(
                        inscription=active_inscription, payment_status="verified"
                    ).aggregate(total=Sum("amount_paid"))["total"]
                    or 0
                )
                
                if total_paid < fees_sheet.base_amount:
                    return False

        return True

    @staticmethod
    def _get_payment_info(student):
        """Get payment amounts for student"""
        # Get active inscription
        active_inscription = (
            Inscription.objects.filter(student=student, regist_status="Active")
            .order_by("-academic_year__start_date")
            .first()
        )

        if not active_inscription:
            return {"amount_paid": 0, "total_amount": 0}

        # Get total amount paid
        amount_paid = (
            Payment.objects.filter(
                inscription=active_inscription, payment_status="verified"
            ).aggregate(total=Sum("amount_paid"))["total"]
            or 0
        )

        # Get total amount required from fees sheets
        total_amount = 0
        
        fees_sheets = StudentDashboardService._get_fees_sheets_for_inscription(active_inscription)
        print(fees_sheets)
        for fees_sheet in fees_sheets:
            # Try to get from payment plans first
            payment_plans = PaymentPlan.objects.filter(feessheet=fees_sheet)
            
            if payment_plans.exists():
                # Sum all payment plan amounts
                plan_total = payment_plans.aggregate(
                    total=Sum("total_amount")
                )["total"] or 0
                total_amount += float(plan_total)
            else:
                # Fall back to fees sheet base amount
                total_amount += float(fees_sheet.base_amount)

        return {
            "amount_paid": float(amount_paid),
            "total_amount": total_amount
        }

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
        """Get student payment history with installments"""
        from services.dependent_service.dashboard_module.dashboard_collection_agent_app.serializers import (
            PaymentSerializer,
            PaymentInstallementSerializer,
        )
        
        # Get student's active inscription
        inscription = Inscription.objects.filter(
            student=student, regist_status="Active"
        ).first()

        if not inscription:
            return {
                "payments": [],
                "installments": []
            }

        # Get payments
        payments = Payment.objects.filter(inscription=inscription).order_by(
            "-payment_date"
        )
        
        # Get payment plan and installments
        installments = []
        try:
            fees_sheets = StudentDashboardService._get_fees_sheets_for_inscription(inscription)
            
            for fees_sheet in fees_sheets:
                payment_plans = PaymentPlan.objects.filter(feessheet=fees_sheet)
                for payment_plan in payment_plans:
                    plan_installments = PaymentInstallement.objects.filter(
                        payment_plan=payment_plan,
                        student=student
                    )
                    installments.extend(plan_installments)
                    
        except Exception:
            # Fallback to get all installments for student
            installments = PaymentInstallement.objects.filter(
                student=student
            )
            
        installments = sorted(installments, key=lambda x: x.due_date)

        return {
            "payments": PaymentSerializer(payments, many=True).data,
            "installments": PaymentInstallementSerializer(installments, many=True).data
        }

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
