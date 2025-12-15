from django.contrib import admin

from .models import (
    CollectionCorrespondence,
    FeesSheet,
    PaymentPlan,
    PaymentPromise,
    PaymentReminder,
)

admin.site.register(FeesSheet)


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
