# Register your models here.

from django.contrib import admin
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
        "principal_teacher",
        "substitute_teacher",
        "academic_year",
        "date_attribution",
        "status_principal_teacher",
        "status_substitute_teacher",
    )
    list_filter = (
        "academic_year",
        "status_principal_teacher",
        "status_substitute_teacher",
    )
    search_fields = (
        "course__name",
        "principal_teacher__user__username",
        "substitute_teacher__user__username",
    )
    readonly_fields = ("id",)
    date_hierarchy = "date_attribution"


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
