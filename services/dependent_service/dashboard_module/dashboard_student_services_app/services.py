from services.core_service.student_module.student_profile_app.models import Student

from .models import (
    AbsenceJustification,
    CounselingSession,
    DocumentRequest,
    Scholarship,
    StudentActivity,
    StudentStatusChange,
)


class StudentServicesService:

    @staticmethod
    def get_dashboard_stats():
        return {
            "total_students": Student.objects.count(),
            "pending_documents": DocumentRequest.objects.filter(
                status="pending"
            ).count(),
            "pending_absences": AbsenceJustification.objects.filter(
                status="pending"
            ).count(),
            "active_scholarships": Scholarship.objects.filter(is_active=True).count(),
            "upcoming_sessions": CounselingSession.objects.count(),
            "active_activities": StudentActivity.objects.filter(
                is_approved=True
            ).count(),
            "pending_status_changes": StudentStatusChange.objects.filter(
                approval_status="pending"
            ).count(),
        }
