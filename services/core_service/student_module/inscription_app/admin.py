# Register your models here.
from django.contrib import admin
from django.db import models
from import_export import fields, resources
from import_export.admin import ImportExportModelAdmin
from import_export.widgets import ForeignKeyWidget
from unfold.admin import ModelAdmin

from services.core_service.academic_module.class_app.models import Class
from services.core_service.academic_module.university_app.models import AcademicYear
from services.core_service.student_module.student_profile_app.models import Student

from .models import Inscription


# ----------------------------
# Inscription Resource
# ----------------------------
class InscriptionResource(resources.ModelResource):
    student_name = fields.Field(
        column_name="student_name",
        attribute="student",
        widget=ForeignKeyWidget(
            Student, "user__email"
        ),  # assuming you want to identify by email
    )
    academic_year_name = fields.Field(
        column_name="academic_year",
        attribute="academic_year",
        widget=ForeignKeyWidget(AcademicYear, "academic_year"),
    )
    class_name = fields.Field(
        column_name="class",
        attribute="class_fk",
        widget=ForeignKeyWidget(Class, "class_name"),
    )

    class Meta:
        model = Inscription
        fields = (
            "id",
            "student",
            "student_name",
            "academic_year",
            "academic_year_name",
            "class_fk",
            "class_name",
            "date_inscription",
            "regist_status",
            "groupe",
            "withdrawal_date",
            "is_year_close",
        )
        export_order = (
            "id",
            "student_name",
            "academic_year",
            "class_name",
            "date_inscription",
            "regist_status",
            "groupe",
            "withdrawal_date",
            "is_year_close",
        )


# ----------------------------
# Inscription Admin
# ----------------------------
@admin.register(Inscription)
class InscriptionAdmin(ImportExportModelAdmin, ModelAdmin):
    resource_class = InscriptionResource
    list_display = (
        "student",
        "academic_year",
        "class_fk",
        "date_inscription",
        "regist_status",
        "groupe",
        "is_year_close",
    )
    search_fields = (
        "student__user__email",
        "academic_year__academic_year",
        "class_fk__class_name",
    )
    list_filter = (
        "academic_year",
        "class_fk",
        "regist_status",
        "groupe",
        "is_year_close",
    )
    ordering = ("date_inscription",)

    fieldsets = (
        (
            "Inscription Information",
            {
                "fields": (
                    "student",
                    "academic_year",
                    "class_fk",
                    "date_inscription",
                    "regist_status",
                    "groupe",
                    "withdrawal_date",
                    "is_year_close",
                )
            },
        ),
    )

    # Optional: Customize Unfold form fields
    formfield_overrides = {
        models.CharField: {
            "widget": admin.widgets.AdminTextInputWidget(attrs={"class": "vTextField"})
        },
    }
