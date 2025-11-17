from django.contrib import admin

from .models import (
    ExamAttendance,
    ExamSession,
    GradeComplaint,
    JuryDecision,
    JurySession,
    OfficialDocument,
    TeacherPaymentClaim,
)

# NOTE: ExamSession and ExamAttendance are dashboard-specific models
# For core exam management, use models from exam_module
# TODO: Consider migrating to use exam_module models to avoid duplication


@admin.register(ExamSession)
class ExamSessionAdmin(admin.ModelAdmin):
    list_display = ["course", "exam_date", "duration_minutes", "room", "created_at"]
    list_filter = ["exam_date", "created_at"]
    search_fields = ["course__course_name", "room"]


@admin.register(ExamAttendance)
class ExamAttendanceAdmin(admin.ModelAdmin):
    list_display = ["exam_session", "student", "status", "recorded_at"]
    list_filter = ["status", "recorded_at"]
    search_fields = ["student__user__email", "student__matricule"]


@admin.register(JurySession)
class JurySessionAdmin(admin.ModelAdmin):
    list_display = ["session_name", "session_date", "status", "created_at"]
    list_filter = ["status", "session_date", "created_at"]
    search_fields = ["session_name"]


@admin.register(JuryDecision)
class JuryDecisionAdmin(admin.ModelAdmin):
    list_display = ["jury_session", "student", "decision", "validated_at"]
    list_filter = ["decision", "validated_at"]
    search_fields = ["student__user__email", "student__matricule"]


@admin.register(GradeComplaint)
class GradeComplaintAdmin(admin.ModelAdmin):
    list_display = ["student", "course", "original_grade", "status", "submitted_at"]
    list_filter = ["status", "submitted_at"]
    search_fields = ["student__user__email", "course__course_name"]


@admin.register(OfficialDocument)
class OfficialDocumentAdmin(admin.ModelAdmin):
    list_display = ["title", "document_type", "status", "created_at", "signed_at"]
    list_filter = ["document_type", "status", "created_at"]
    search_fields = ["title", "content"]


@admin.register(TeacherPaymentClaim)
class TeacherPaymentClaimAdmin(admin.ModelAdmin):
    list_display = [
        "teacher",
        "course",
        "hours_taught",
        "total_amount",
        "status",
        "submitted_at",
    ]
    list_filter = ["status", "submitted_at"]
    search_fields = ["teacher__user__email", "course__course_name"]
