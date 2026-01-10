from django.contrib import admin

from services.core_service.academic_module.teacher_app.models import Attribution

admin.site.unregister(Attribution)

@admin.register(Attribution)
class AttributionAdmin(admin.ModelAdmin):
    """
    Admin configuration for Attribution model.
    This model is used to track teacher attributions and their validations by academic administrators.
    """
    
    list_display = [
        "id",
        "get_teacher",
        "get_course",
        "get_academic_year",
        "get_validated_by",
        "status_principal_teacher",
        "status_substitute_teacher",
        "validation_date",
        "date_attribution",
    ]
    list_filter = [
        "status_principal_teacher",
        "status_substitute_teacher",
        "validation_date",
        "academic_year",
        "date_attribution",
    ]
    search_fields = [
        "principal_teacher__user__email",
        "principal_teacher__user__first_name",
        "principal_teacher__user__last_name",
        "course__course_name",
        "course__course_code",
        "validated_by__email",
        "validated_by__first_name",
        "validated_by__last_name",
        "validation_comments",
    ]
    readonly_fields = [
        "id",
        "validation_date",
        "date_attribution",
    ]
    ordering = ["-validation_date", "-id"]
    
    def get_teacher(self, obj):
        """Get the teacher name from the attribution."""
        if obj.principal_teacher:
            teacher = obj.principal_teacher
            if teacher.user:
                return f"{teacher.user.first_name} {teacher.user.last_name}"
            return str(teacher)
        return None
    
    get_teacher.short_description = "Teacher"
    get_teacher.admin_order_field = "principal_teacher__user__last_name"
    
    def get_course(self, obj):
        """Get the course name from the attribution."""
        if obj.course:
            return f"{obj.course.course_code} - {obj.course.course_name}"
        return None
    
    get_course.short_description = "Course"
    get_course.admin_order_field = "course__course_name"
    
    def get_academic_year(self, obj):
        """Get the academic year."""
        if obj.academic_year:
            return str(obj.academic_year)
        return None
    
    get_academic_year.short_description = "Academic Year"
    get_academic_year.admin_order_field = "academic_year__start_year"
    
    def get_validated_by(self, obj):
        """Get the name of the user who validated."""
        if obj.validated_by:
            return f"{obj.validated_by.first_name} {obj.validated_by.last_name}"
        return None
    
    get_validated_by.short_description = "Validated By"
    get_validated_by.admin_order_field = "validated_by__last_name"
    
    fieldsets = (
        (
            "Attribution Information",
            {
                "fields": (
                    "id",
                    "course",
                    "principal_teacher",
                    "substitute_teacher",
                    "academic_year",
                    "date_attribution",
                )
            },
        ),
        (
            "Teacher Status",
            {
                "fields": (
                    "status_principal_teacher",
                    "status_substitute_teacher",
                    "commentaire",
                )
            },
        ),
        (
            "Validation Information",
            {
                "fields": (
                    "validated_by",
                    "validation_date",
                    "validation_comments",
                )
            },
        ),
        (
            "Authorization",
            {
                "fields": (
                    "submitted_by",
                    "authorized_by",
                ),
                "classes": ("collapse",),
            },
        ),
    )

