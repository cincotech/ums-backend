# Register your models here.
from django.contrib import admin
from django.db import models
from import_export import fields, resources
from import_export.admin import ImportExportModelAdmin
from import_export.widgets import ForeignKeyWidget
from unfold.admin import ModelAdmin

from services.core_service.student_module.student_profile_app.models import Student

from .models import StudentCard, StudentCardLog


# ----------------------------
# StudentCard Resource
# ----------------------------
class StudentCardResource(resources.ModelResource):
    student_email = fields.Field(
        column_name="student_email",
        attribute="student",
        widget=ForeignKeyWidget(
            Student, "user__email"
        ),  # assuming Student linked to User
    )

    class Meta:
        model = StudentCard
        fields = (
            "id",
            "student",
            "student_email",
            "card_number",
            "issue_date",
            "expiry_date",
            "status",
            "printed_by",
            "photo_url",
            "qrcode_data",
        )
        export_order = (
            "id",
            "student_email",
            "card_number",
            "issue_date",
            "expiry_date",
            "status",
            "printed_by",
            "photo_url",
            "qrcode_data",
        )


# ----------------------------
# StudentCardLog Resource
# ----------------------------
class StudentCardLogResource(resources.ModelResource):
    card_number = fields.Field(
        column_name="card_number",
        attribute="card",
        widget=ForeignKeyWidget(StudentCard, "card_number"),
    )

    class Meta:
        model = StudentCardLog
        fields = (
            "id",
            "card",
            "card_number",
            "action",
            "action_date",
            "performed_by",
            "remarks",
        )
        export_order = (
            "id",
            "card_number",
            "action",
            "action_date",
            "performed_by",
            "remarks",
        )


# ----------------------------
# Admin Registration
# ----------------------------
@admin.register(StudentCard)
class StudentCardAdmin(ImportExportModelAdmin, ModelAdmin):
    resource_class = StudentCardResource
    list_display = ("card_number", "student", "issue_date", "expiry_date", "status")
    list_filter = ("status",)
    search_fields = ("card_number", "student__user__email")
    ordering = ("issue_date",)
    fieldsets = (
        (
            "Card Information",
            {
                "fields": (
                    "student",
                    "card_number",
                    "issue_date",
                    "expiry_date",
                    "status",
                    "printed_by",
                    "photo_url",
                    "qrcode_data",
                )
            },
        ),
    )
    formfield_overrides = {
        models.CharField: {
            "widget": admin.widgets.AdminTextInputWidget(attrs={"class": "vTextField"})
        },
    }


@admin.register(StudentCardLog)
class StudentCardLogAdmin(ImportExportModelAdmin, ModelAdmin):
    resource_class = StudentCardLogResource
    list_display = ("card", "action", "action_date", "performed_by")
    list_filter = ("action",)
    search_fields = ("card__card_number", "performed_by")
    ordering = ("-action_date",)
    fieldsets = (
        ("Log Information", {"fields": ("card", "action", "performed_by", "remarks")}),
    )
    formfield_overrides = {
        models.CharField: {
            "widget": admin.widgets.AdminTextInputWidget(attrs={"class": "vTextField"})
        },
    }
