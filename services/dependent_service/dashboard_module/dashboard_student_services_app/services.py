from datetime import timedelta

from django.db.models import Count
from django.utils import timezone

from services.core_service.student_module.inscription_app.models import Inscription
from services.core_service.student_module.student_profile_app.models import Student
from services.dependent_service.exam_module.result_app.models import CompiledResult

from .models import (
    AbsenceJustification,
    CounselingSession,
    DocumentRequest,
    Scholarship,
    StudentActivity,
)


class StudentServicesService:

    @staticmethod
    def get_dashboard_stats():
        """Get student services dashboard overview"""
        total_students = Student.objects.count()
        pending_documents = DocumentRequest.objects.filter(status="pending").count()
        pending_absences = AbsenceJustification.objects.filter(status="pending").count()
        active_scholarships = Scholarship.objects.filter(is_active=True).count()

        upcoming_sessions = CounselingSession.objects.filter(
            scheduled_date__gte=timezone.now(),
            scheduled_date__lte=timezone.now() + timedelta(days=7),
        ).count()

        active_activities = StudentActivity.objects.filter(
            is_approved=True,
            start_date__lte=timezone.now(),
            end_date__gte=timezone.now(),
        ).count()

        return {
            "total_students": total_students,
            "pending_documents": pending_documents,
            "pending_absences": pending_absences,
            "active_scholarships": active_scholarships,
            "upcoming_sessions": upcoming_sessions,
            "active_activities": active_activities,
        }

    @staticmethod
    def manage_enrollment(student_data, user):
        """Handle new student enrollment"""
        # This would integrate with existing inscription system
        # Simplified implementation
        student = Student.objects.create(**student_data)
        return student

    @staticmethod
    def process_document_request(request_id, action, notes, user):
        """Process document request (approve/reject/complete)"""
        doc_request = DocumentRequest.objects.get(id=request_id)

        if action in ["processing", "ready", "delivered", "rejected"]:
            doc_request.status = action
            doc_request.notes = notes
            doc_request.processed_by = user
            doc_request.processed_at = timezone.now()
            doc_request.save()

        return doc_request

    @staticmethod
    def process_absence_justification(absence_id, decision, user):
        """Process absence justification (approve/reject)"""
        absence = AbsenceJustification.objects.get(id=absence_id)
        absence.status = decision
        absence.reviewed_by = user
        absence.reviewed_at = timezone.now()
        absence.save()

        return absence

    @staticmethod
    def manage_scholarship(student_id, scholarship_data, user):
        """Add or update scholarship information"""
        scholarship_data["student_id"] = student_id
        scholarship_data["managed_by"] = user

        scholarship = Scholarship.objects.create(**scholarship_data)
        return scholarship

    @staticmethod
    def schedule_counseling_session(session_data, user):
        """Schedule orientation or counseling session"""
        session_data["counselor"] = user
        session = CounselingSession.objects.create(**session_data)
        return session

    @staticmethod
    def approve_student_activity(activity_id, user):
        """Approve student club/activity"""
        activity = StudentActivity.objects.get(id=activity_id)
        activity.is_approved = True
        activity.approved_by = user
        activity.save()

        return activity

    @staticmethod
    def generate_enrollment_report(academic_year=None):
        """Generate enrollment statistics and reports"""
        queryset = Inscription.objects.all()
        if academic_year:
            queryset = queryset.filter(academic_year__year=academic_year)

        total_enrolled = queryset.count()

        # By program distribution
        by_program = queryset.values(
            "student__graduate_infos__department__name"
        ).annotate(count=Count("id"))

        program_distribution = {
            item["student__graduate_infos__department__name"]
            or "Unassigned": item["count"]
            for item in by_program
        }

        # By level (simplified)
        by_level = {"L1": 0, "L2": 0, "L3": 0, "M1": 0, "M2": 0}

        # Success rate calculation
        passed_students = CompiledResult.objects.filter(status="passed").count()
        success_rate = (
            (passed_students / total_enrolled * 100) if total_enrolled > 0 else 0
        )

        # Retention rate (students who re-enrolled)
        current_students = Student.objects.count()
        retention_rate = (
            (current_students / total_enrolled * 100) if total_enrolled > 0 else 0
        )

        return {
            "academic_year": academic_year or "Current",
            "total_enrolled": total_enrolled,
            "by_program": program_distribution,
            "by_level": by_level,
            "success_rate": round(success_rate, 2),
            "retention_rate": round(retention_rate, 2),
        }

    @staticmethod
    def get_student_population_data():
        """Generate student population data by year and class"""
        population_data = []

        # Group by academic year and program
        inscriptions = Inscription.objects.values(
            "academic_year__year", "student__graduate_infos__department__name"
        ).annotate(count=Count("id"))

        for item in inscriptions:
            population_data.append(
                {
                    "academic_year": item["academic_year__year"],
                    "program": item["student__graduate_infos__department__name"]
                    or "Unassigned",
                    "student_count": item["count"],
                }
            )

        return population_data

    @staticmethod
    def update_student_profile(student_id, profile_data, user):
        """Update student personal and administrative information"""
        student = Student.objects.get(id=student_id)

        # Update user information
        for key, value in profile_data.items():
            if hasattr(student.user, key):
                setattr(student.user, key, value)
            elif hasattr(student, key):
                setattr(student, key, value)

        student.user.save()
        student.save()

        return student
