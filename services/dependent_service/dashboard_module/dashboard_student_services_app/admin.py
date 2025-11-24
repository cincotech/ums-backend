# from django.contrib import admin

# from .models import (
#     AbsenceJustification,
#     CounselingSession,
#     DocumentRequest,
#     Scholarship,
#     StudentActivity,
# )


# @admin.register(DocumentRequest)
# class DocumentRequestAdmin(admin.ModelAdmin):
#     list_display = [
#         "student",
#         "document_type",
#         "status",
#         "requested_at",
#         "processed_at",
#     ]
#     list_filter = ["document_type", "status", "requested_at"]
#     search_fields = ["student__user__email", "student__matricule"]


# @admin.register(AbsenceJustification)
# class AbsenceJustificationAdmin(admin.ModelAdmin):
#     list_display = ["student", "absence_type", "start_date", "end_date", "status"]
#     list_filter = ["absence_type", "status", "submitted_at"]
#     search_fields = ["student__user__email", "student__matricule"]


# @admin.register(StudentActivity)
# class StudentActivityAdmin(admin.ModelAdmin):
#     list_display = ["name", "activity_type", "organizer", "start_date", "is_approved"]
#     list_filter = ["activity_type", "is_approved", "start_date"]
#     search_fields = ["name", "organizer__user__email"]


# @admin.register(Scholarship)
# class ScholarshipAdmin(admin.ModelAdmin):
#     list_display = [
#         "student",
#         "scholarship_type",
#         "provider",
#         "amount",
#         "academic_year",
#         "is_active",
#     ]
#     list_filter = ["scholarship_type", "is_active", "academic_year"]
#     search_fields = ["student__user__email", "provider"]


# @admin.register(CounselingSession)
# class CounselingSessionAdmin(admin.ModelAdmin):
#     list_display = [
#         "title",
#         "session_type",
#         "counselor",
#         "scheduled_date",
#         "is_group_session",
#     ]
#     list_filter = ["session_type", "is_group_session", "scheduled_date"]
#     search_fields = ["title", "counselor__email"]
