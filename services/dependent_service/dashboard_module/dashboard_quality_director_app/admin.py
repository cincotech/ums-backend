# from django.contrib import admin

# from .models import ComplianceAudit, QualityStandard, StudentSurvey


# @admin.register(StudentSurvey)
# class StudentSurveyAdmin(admin.ModelAdmin):
#     list_display = [
#         "survey_type",
#         "student",
#         "course",
#         "teacher",
#         "rating",
#         "submitted_at",
#     ]
#     list_filter = ["survey_type", "rating", "submitted_at"]
#     search_fields = ["student__user__email", "course__course_name"]


# @admin.register(QualityStandard)
# class QualityStandardAdmin(admin.ModelAdmin):
#     list_display = ["title", "standard_type", "is_active", "created_at"]
#     list_filter = ["standard_type", "is_active", "created_at"]
#     search_fields = ["title", "description"]


# @admin.register(ComplianceAudit)
# class ComplianceAuditAdmin(admin.ModelAdmin):
#     list_display = ["standard", "compliance_status", "audited_by", "audit_date"]
#     list_filter = ["compliance_status", "audit_date"]
#     search_fields = ["standard__title", "audited_by__email"]
