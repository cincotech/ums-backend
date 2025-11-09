from django.contrib import admin
from import_export import resources
from import_export.admin import ImportExportModelAdmin
from simple_history.admin import SimpleHistoryAdmin
from unfold.admin import ModelAdmin

from .models import Bank, Payment


class BankResource(resources.ModelResource):
    class Meta:
        model = Bank
        fields = ("bank_name", "bank_abreviation")
        export_order = ("id", "bank_name", "bank_abreviation")


class PaymentResource(resources.ModelResource):
    class Meta:
        model = Payment
        fields = (
            "id",
            "feessheet",
            "amount_paid",
            "payment_date",
            "reception_date",
            "payment_method",
            "bank",
            "bank_slip_ref",
            "transaction_code",
            "inscription",
            "user",
            "description",
            "remittance_slip_uri",
            "payment_status",
        )
        export_order = fields


@admin.register(Bank)
class BankAdmin(ImportExportModelAdmin, SimpleHistoryAdmin, ModelAdmin):
    resource_class = BankResource
    list_display = ("bank_name", "bank_abreviation")
    search_fields = ("bank_name", "bank_abreviation")
    list_filter = ("bank_abreviation",)
    history_list_display = ["bank_name"]  # for unfold's history view
    ordering = ("bank_name",)


@admin.register(Payment)
class PaymentAdmin(ImportExportModelAdmin, SimpleHistoryAdmin, ModelAdmin):
    resource_class = PaymentResource
    list_display = (
        "feessheet",
        "amount_paid",
        "payment_method",
        "bank",
        "payment_status",
        "user",
        "payment_date",
        "reception_date",
    )
    list_filter = ("payment_method", "payment_status", "bank")
    search_fields = (
        "transaction_code",
        "bank_slip_ref",
        "description",
        "user__username",
    )
    history_list_display = ["payment_status"]
    date_hierarchy = "payment_date"
    ordering = ("-payment_date",)
