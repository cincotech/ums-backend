# Register your models here.
from django.contrib import admin
from django.db import models
from import_export import fields, resources
from import_export.admin import ImportExportModelAdmin
from import_export.widgets import ForeignKeyWidget
from unfold.admin import ModelAdmin

from services.core_service.finance_module.fees_app.models import FeesSheet
from services.core_service.student_module.inscription_app.models import Inscription

from .models import DebtCancellation


# ----------------------------
# DebtCancellation Resource
# ----------------------------
class DebtCancellationResource(resources.ModelResource):
    inscription_number = fields.Field(
        column_name="inscription_number",
        attribute="inscription",
        widget=ForeignKeyWidget(Inscription, "id"),  # or 'student_number' if available
    )
    feesheet_name = fields.Field(
        column_name="feesheet",
        attribute="feessheet",
        widget=ForeignKeyWidget(FeesSheet, "id"),  # or any readable field
    )

    class Meta:
        model = DebtCancellation
        fields = (
            "id",
            "inscription",
            "inscription_number",
            "feessheet",
            "feesheet_name",
            "cancelation_date",
            "cancelled_amount",
            "reason",
        )
        export_order = (
            "id",
            "inscription_number",
            "feesheet_name",
            "cancelation_date",
            "cancelled_amount",
            "reason",
        )


# ----------------------------
# DebtCancellation Admin
# ----------------------------
@admin.register(DebtCancellation)
class DebtCancellationAdmin(ImportExportModelAdmin, ModelAdmin):
    resource_class = DebtCancellationResource
    list_display = (
        "inscription",
        "feessheet",
        "cancelation_date",
        "cancelled_amount",
        "reason",
    )
    list_filter = ("cancelation_date",)
    search_fields = ("inscription__id", "feessheet__id", "reason")
    ordering = ("cancelation_date",)

    fieldsets = (
        (
            "Debt Cancellation Information",
            {
                "fields": (
                    "inscription",
                    "feessheet",
                    "cancelation_date",
                    "cancelled_amount",
                    "reason",
                )
            },
        ),
    )

    formfield_overrides = {
        models.PositiveIntegerField: {
            "widget": admin.widgets.AdminIntegerFieldWidget(
                attrs={"class": "vIntegerField"}
            )
        },
        models.TextField: {
            "widget": admin.widgets.AdminTextareaWidget(attrs={"rows": 3, "cols": 40})
        },
    }
