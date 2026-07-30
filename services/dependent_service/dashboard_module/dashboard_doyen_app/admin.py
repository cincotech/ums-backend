from django.contrib import admin

from .models import (
    CurriculumCourse,
    CurriculumTeachingUnit,
    CurriculumTemplate,
    SecretaryNote,
    TeacherWorkload,
    TeachingProgress,
)


@admin.register(TeachingProgress)
class TeachingProgressAdmin(admin.ModelAdmin):
    list_display = (
        "attribution",
        "faculty",
        "progress_percentage",
        "last_updated",
        "submitted_by",
    )
    list_filter = ("faculty", "last_updated")
    search_fields = (
        "attribution__course__course_name",
        "attribution__course__course_code",
    )
    readonly_fields = ("id", "last_updated", "progress_percentage")

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        return qs.select_related("attribution", "faculty", "submitted_by")


@admin.register(TeacherWorkload)
class TeacherWorkloadAdmin(admin.ModelAdmin):
    list_display = (
        "teacher",
        "faculty",
        "academic_year",
        "total_hours",
        "assigned_hours",
        "is_permanent",
        "workload_status",
    )
    list_filter = ("faculty", "academic_year", "is_permanent")
    search_fields = ("teacher__first_name", "teacher__last_name", "teacher__email")
    readonly_fields = ("id", "assigned_hours")

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        return qs.select_related("teacher", "faculty", "academic_year")

    def workload_status(self, obj):
        if obj.total_hours == 0:
            return "N/A"
        percentage = (float(obj.assigned_hours) / obj.total_hours) * 100
        if percentage > 100:
            return f"Overloaded ({percentage:.1f}%)"
        elif percentage < 70:
            return f"Underutilized ({percentage:.1f}%)"
        else:
            return f"Balanced ({percentage:.1f}%)"

    workload_status.short_description = "Workload Status"


@admin.register(SecretaryNote)
class SecretaryNoteAdmin(admin.ModelAdmin):
    list_display = (
        "subject",
        "faculty",
        "created_by",
        "created_date",
        "is_resolved",
    )
    list_filter = ("faculty", "is_resolved", "created_date")
    search_fields = ("subject", "message")
    readonly_fields = ("id", "created_date")

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        return qs.select_related("faculty", "created_by")


class CurriculumCourseInline(admin.TabularInline):
    model = CurriculumCourse
    extra = 0


@admin.register(CurriculumTeachingUnit)
class CurriculumTeachingUnitAdmin(admin.ModelAdmin):
    list_display = ("template", "module", "position", "is_required")
    list_filter = ("template__status", "is_required")
    inlines = [CurriculumCourseInline]


@admin.register(CurriculumTemplate)
class CurriculumTemplateAdmin(admin.ModelAdmin):
    list_display = (
        "title",
        "class_fk",
        "academic_year",
        "semester",
        "version",
        "status",
    )
    list_filter = ("status", "academic_year", "semester")
    search_fields = ("title", "class_fk__class_name")
    readonly_fields = ("created_at", "updated_at", "published_at")
