from django.contrib import admin
from django.utils import timezone

from services.core_service.academic_module.teacher_app.models import Attribution

admin.site.unregister(Attribution)


def validate_principal_teacher(modeladmin, request, queryset):
    """
    Action pour valider le professeur principal.
    Le professeur principal devient Accepted et le remplaçant devient Refused.
    """
    for attribution in queryset:
        attribution.status_principal_teacher = Attribution.STATUS_ACCEPTED
        attribution.status_substitute_teacher = Attribution.STATUS_REFUSED
        attribution.validated_by = request.user
        attribution.validation_date = timezone.now()
        attribution.save()
    modeladmin.message_user(
        request,
        "Professeur principal validé avec succès. Le professeur remplaçant a été automatiquement refusé.",
    )


def validate_substitute_teacher(modeladmin, request, queryset):
    """
    Action pour valider le professeur remplaçant.
    Le professeur remplaçant devient Accepted et le principal devient Refused.
    """
    for attribution in queryset:
        attribution.status_substitute_teacher = Attribution.STATUS_ACCEPTED
        attribution.status_principal_teacher = Attribution.STATUS_REFUSED
        attribution.validated_by = request.user
        attribution.validation_date = timezone.now()
        attribution.save()
    modeladmin.message_user(
        request,
        "Professeur remplaçant validé avec succès. Le professeur principal a été automatiquement refusé.",
    )


def reset_to_pending(modeladmin, request, queryset):
    """
    Action pour réinitialiser les statuts à Pending.
    """
    for attribution in queryset:
        attribution.status_principal_teacher = Attribution.STATUS_PENDING
        attribution.status_substitute_teacher = Attribution.STATUS_PENDING
        attribution.validated_by = None
        attribution.validation_date = None
        attribution.save()
    modeladmin.message_user(request, "Statuts réinitialisés à Pending.")


validate_principal_teacher.short_description = (
    "Valider le professeur principal (Remplaçant = Refused)"
)
validate_substitute_teacher.short_description = (
    "Valider le professeur remplaçant (Principal = Refused)"
)
reset_to_pending.short_description = "Réinitialiser à Pending"


@admin.register(Attribution)
class AttributionAdmin(admin.ModelAdmin):
    """
    Admin configuration for Attribution model.
    This model is used to track teacher attributions and their validations by academic administrators.
    One course = 2 teachers (principal + substitute) with default Pending status.
    When academic validates one teacher, the other automatically gets Refused.
    """

    list_display = [
        "id",
        "get_course",
        "get_principal_teacher",
        "status_principal_teacher",
        "get_substitute_teacher",
        "status_substitute_teacher",
        "get_academic_year",
        "date_attribution",
    ]
    list_filter = [
        "status_principal_teacher",
        "status_substitute_teacher",
        "academic_year",
        "date_attribution",
    ]
    search_fields = [
        "principal_teacher__user__email",
        "principal_teacher__user__first_name",
        "principal_teacher__user__last_name",
        "substitute_teacher__user__email",
        "substitute_teacher__user__first_name",
        "substitute_teacher__user__last_name",
        "course__course_name",
        "course__course_code",
    ]
    readonly_fields = [
        "id",
        "validation_date",
        "date_attribution",
    ]
    ordering = ["-date_attribution", "-id"]
    actions = [
        validate_principal_teacher,
        validate_substitute_teacher,
        reset_to_pending,
    ]

    def get_queryset(self, request):
        """Optimize queryset with select_related for foreign keys."""
        queryset = super().get_queryset(request)
        queryset = queryset.select_related(
            "course",
            "principal_teacher",
            "principal_teacher__user",
            "substitute_teacher",
            "substitute_teacher__user",
            "academic_year",
            "validated_by",
            "submitted_by",
            "authorized_by",
        )
        return queryset

    def get_principal_teacher(self, obj):
        """Get the principal teacher name."""
        if obj.principal_teacher:
            teacher = obj.principal_teacher
            if teacher.user:
                return f"{teacher.user.first_name} {teacher.user.last_name}"
            return f"Teacher (ID: {teacher.id})"
        return "—"

    get_principal_teacher.short_description = "Teacher Principal"
    get_principal_teacher.admin_order_field = "principal_teacher__user__last_name"

    def get_substitute_teacher(self, obj):
        """Get the substitute teacher name."""
        if obj.substitute_teacher:
            teacher = obj.substitute_teacher
            if teacher.user:
                return f"{teacher.user.first_name} {teacher.user.last_name}"
            return f"Teacher (ID: {teacher.id})"
        return "—"

    get_substitute_teacher.short_description = "Teacher Remplaçant"
    get_substitute_teacher.admin_order_field = "substitute_teacher__user__last_name"

    def get_course(self, obj):
        """Get the course name."""
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

    get_academic_year.short_description = "Année"
    get_academic_year.admin_order_field = "academic_year__start_year"

    fieldsets = (
        (
            "Information d'Attribution",
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
            "Statut des Enseignants",
            {
                "description": "Lorsqu'un enseignant est validé, l'autre est automatiquement refusé.",
                "fields": (
                    "status_principal_teacher",
                    "status_substitute_teacher",
                    "commentaire",
                ),
            },
        ),
        (
            "Information de Validation",
            {
                "fields": (
                    "validated_by",
                    "validation_date",
                    "validation_comments",
                )
            },
        ),
        (
            "Autorisation",
            {
                "fields": (
                    "submitted_by",
                    "authorized_by",
                ),
                "classes": ("collapse",),
            },
        ),
    )
