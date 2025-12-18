from django.contrib import admin

from .models import (
    Bank,
    CollectionCorrespondence,
    FeesSheet,
    Payment,
    PaymentInstallement,
    PaymentPlan,
    PaymentPromise,
    PaymentReminder,
    Wording,
)


@admin.register(Bank)
class BankAdmin(admin.ModelAdmin):
    list_display = ["bank_name", "bank_abreviation"]
    search_fields = ["bank_name", "bank_abreviation"]


@admin.register(Wording)
class WordingAdmin(admin.ModelAdmin):
    list_display = ["wording_name"]
    search_fields = ["wording_name"]


@admin.register(FeesSheet)
class FeesSheetAdmin(admin.ModelAdmin):
    list_display = [
        "wording",
        "class_fk",
        "department",
        "faculty",
        "academic_year",
        "base_amount",
    ]
    list_filter = ["academic_year", "wording"]
    search_fields = [
        "wording__wording_name",
        "class_fk__class_name",
        "department__department_name",
        "faculty__faculty_name",
    ]


@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = [
        "user",
        "paymentplan",
        "amount_paid",
        "payment_method",
        "payment_status",
        "payment_date",
    ]
    list_filter = ["payment_method", "payment_status", "payment_date"]
    search_fields = ["user__email", "bank_slip_ref", "transaction_code"]


@admin.register(PaymentInstallement)
class PaymentInstallementAdmin(admin.ModelAdmin):
    list_display = [
        "student",
        "payment_plan",
        "amount",
        "due_date",
        "status",
        "paid_amount",
    ]
    list_filter = ["status", "due_date"]
    search_fields = ["student__user__email", "student__matricule"]


@admin.register(PaymentReminder)
class PaymentReminderAdmin(admin.ModelAdmin):
    list_display = ["student", "reminder_type", "amount_due", "status", "sent_at"]
    list_filter = ["reminder_type", "status", "sent_at"]
    search_fields = ["student__user__email", "student__matricule"]


@admin.register(PaymentPlan)
class PaymentPlanAdmin(admin.ModelAdmin):
    list_display = [
        "feessheet",
        "total_amount",
        "monthly_amount",
        "start_date",
        "end_date",
        "status",
    ]
    list_filter = ["status", "start_date", "created_at"]
    search_fields = ["student__user__email", "student__matricule"]


@admin.register(PaymentPromise)
class PaymentPromiseAdmin(admin.ModelAdmin):
    list_display = [
        "student",
        "promised_amount",
        "promised_date",
        "status",
        "recorded_at",
    ]
    list_filter = ["status", "promised_date", "recorded_at"]
    search_fields = ["student__user__email", "student__matricule"]


@admin.register(CollectionCorrespondence)
class CollectionCorrespondenceAdmin(admin.ModelAdmin):
    list_display = ["student", "correspondence_type", "subject", "sent_at"]
    list_filter = ["correspondence_type", "sent_at"]
    search_fields = ["student__user__email", "subject"]
