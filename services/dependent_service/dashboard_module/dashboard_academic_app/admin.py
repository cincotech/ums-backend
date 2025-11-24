# from django.contrib import admin

# from .models import AttributionValidation, QualityReport


# @admin.register(QualityReport)
# class QualityReportAdmin(admin.ModelAdmin):
#     list_display = ["title", "report_type", "generated_by", "generated_date"]
#     list_filter = ["report_type", "generated_date"]
#     search_fields = ["title", "generated_by__email"]
#     readonly_fields = ["generated_date"]


# @admin.register(AttributionValidation)
# class AttributionValidationAdmin(admin.ModelAdmin):
#     list_display = [
#         "attribution",
#         "validation_status",
#         "validated_by",
#         "validation_date",
#     ]
#     list_filter = ["validation_status", "validation_date"]
#     search_fields = ["attribution__course__course_name", "validated_by__email"]
#     readonly_fields = ["validation_date"]
