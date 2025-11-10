# Register your models here.
from django.contrib import admin
from django.db import models
from import_export import fields, resources, widgets
from import_export.admin import ImportExportModelAdmin
from unfold.admin import ModelAdmin

from services.core_service.student_module.card_app.models import StudentCard
from services.core_service.student_module.inscription_app.models import Inscription
from services.dependent_service.exam_module.exam_app.models import ExamRoom

from .models import ExamAttendance


# ----------------------------
# Resource for Import/Export
# ----------------------------
class ExamAttendanceResource(resources.ModelResource):
    examroom_id = fields.Field(
        column_name="examroom_id",
        attribute="examroom",
        widget=widgets.ForeignKeyWidget(ExamRoom, "id"),
    )
    card_number = fields.Field(
        column_name="card_number",
        attribute="card",
        widget=widgets.ForeignKeyWidget(StudentCard, "card_number"),
    )
    inscription_id = fields.Field(
        column_name="inscription_id",
        attribute="inscription",
        widget=widgets.ForeignKeyWidget(Inscription, "id"),
    )

    class Meta:
        model = ExamAttendance
        fields = (
            "id",
            "examroom_id",
            "card_number",
            "inscription_id",
            "attendance_time",
            "status",
        )
        export_order = (
            "id",
            "examroom_id",
            "card_number",
            "inscription_id",
            "attendance_time",
            "status",
        )


# ----------------------------
# Admin class
# ----------------------------
@admin.register(ExamAttendance)
class ExamAttendanceAdmin(ImportExportModelAdmin, ModelAdmin):
    resource_class = ExamAttendanceResource
    list_display = ("examroom", "card", "inscription", "attendance_time", "status")
    list_filter = ("status", "examroom")
    search_fields = ("card__card_number", "inscription__student__matricule")
    ordering = ("-attendance_time",)

    formfield_overrides = {
        models.CharField: {
            "widget": admin.widgets.AdminTextInputWidget(attrs={"class": "vTextField"})
        },
    }
