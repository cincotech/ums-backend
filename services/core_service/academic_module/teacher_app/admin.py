# Register your models here.

from django.contrib import admin, messages
from django.contrib.admin import helpers
from django.http import HttpResponseRedirect
from django.shortcuts import render
from django.utils.translation import ngettext
from unfold.admin import ModelAdmin

from .models import Attribution, Suggestion, Teacher


@admin.register(Teacher)
class TeacherAdmin(ModelAdmin):
    list_display = (
        "id",
        "user",
        "teacher_grade",
        "degree",
        "university",
        "speciality",
    )
    list_filter = ("degree", "university")
    search_fields = (
        "user__username",
        "user__email",
        "teacher_grade",
        "speciality",
    )
    readonly_fields = ("id",)


@admin.register(Attribution)
class AttributionAdmin(ModelAdmin):
    list_display = (
        "id",
        "course",
        "principal_teacher_name",
        "status_principal_teacher",
        "substitute_teacher_name",
        "status_substitute_teacher",
        "academic_year",
        "date_attribution",
    )

    list_filter = (
        "academic_year",
        "status_principal_teacher",
        "status_substitute_teacher",
    )

    search_fields = (
        "course__name",
        "principal_teacher__user__first_name",
        "principal_teacher__user__last_name",
        "substitute_teacher__user__first_name",
        "substitute_teacher__user__last_name",
    )

    autocomplete_fields = ["principal_teacher", "substitute_teacher"]

    readonly_fields = ("id", "date_attribution")

    date_hierarchy = "date_attribution"

    actions = ["delete_selected_attributions"]

    def delete_selected_attributions(self, request, queryset):
        """
        Custom delete action with confirmation page
        """
        if request.POST.get("post"):
            # Delete the selected objects
            deleted_count = 0
            for obj in queryset:
                obj.delete()
                deleted_count += 1

            self.message_user(
                request,
                ngettext(
                    "%d attribution was successfully deleted.",
                    "%d attributions were successfully deleted.",
                    deleted_count,
                )
                % deleted_count,
                messages.SUCCESS,
            )
            return HttpResponseRedirect(request.get_full_path())

        # Show confirmation page
        context = {
            "title": "Are you sure?",
            "queryset": queryset,
            "action_checkbox_name": helpers.ACTION_CHECKBOX_NAME,
            "opts": self.model._meta,
            "action_name": "delete_selected_attributions",
            "app_label": self.model._meta.app_label,
            "model_name": self.model._meta.model_name,
        }
        return render(request, "admin/delete_selected_confirmation.html", context)

    delete_selected_attributions.short_description = "Delete selected attributions"

    def get_queryset(self, request):
        return (
            super()
            .get_queryset(request)
            .select_related(
                "principal_teacher__user",
                "substitute_teacher__user",
                "course",
                "academic_year",
            )
        )

    @admin.display(description="Teacher Principal")
    def principal_teacher_name(self, obj):
        if not obj.principal_teacher:
            return "—"
        user = obj.principal_teacher.user
        return f"{user.first_name} {user.last_name}".strip() or user.email

    @admin.display(description="Teacher Remplaçant")
    def substitute_teacher_name(self, obj):
        if not obj.substitute_teacher:
            return "—"
        user = obj.substitute_teacher.user
        return f"{user.first_name} {user.last_name}".strip() or user.email

    @admin.display(description="Année")
    def academic_year_display(self, obj):
        return obj.academic_year or "—"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Ensure proper ordering of columns in the list view
        self.list_display_links = (None,)


@admin.register(Suggestion)
class SuggestionAdmin(ModelAdmin):
    list_display = (
        "id",
        "suggestion_date",
        "teacher",
        "user",
        "attribution",
    )
    list_filter = ("suggestion_date",)
    search_fields = (
        "teacher__user__username",
        "user__username",
        "suggestion",
    )
    readonly_fields = ("id",)
