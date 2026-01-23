from django.contrib import admin
from import_export import resources
from import_export.admin import ImportExportModelAdmin
from unfold.admin import ModelAdmin

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


# ----------------------------
# Resources
# ----------------------------
class BankResource(resources.ModelResource):
    class Meta:
        model = Bank
        fields = ("id", "bank_name", "bank_abreviation", "account_number", "status")


class WordingResource(resources.ModelResource):
    class Meta:
        model = Wording
        fields = ("id", "wording_name")


class FeesSheetResource(resources.ModelResource):
    level_type = resources.Field()
    level_name = resources.Field()

    class Meta:
        model = FeesSheet
        fields = (
            "id",
            "wording",
            "academic_year",
            "base_amount",
            "level_type",
            "level_name",
        )
        export_order = (
            "id",
            "wording",
            "academic_year",
            "level_type",
            "level_name",
            "base_amount",
        )

    def dehydrate_level_type(self, feessheet):
        if feessheet.class_fk:
            return "Classe"
        elif feessheet.department:
            return "Département"
        elif feessheet.faculty:
            return "Faculté"
        return "Non défini"

    def dehydrate_level_name(self, feessheet):
        if feessheet.class_fk:
            return feessheet.class_fk.class_name
        elif feessheet.department:
            return feessheet.department.department_name
        elif feessheet.faculty:
            return feessheet.faculty.faculty_name
        return "Non défini"


class PaymentPlanResource(resources.ModelResource):
    class Meta:
        model = PaymentPlan
        fields = (
            "id",
            "feessheet",
            "total_amount",
            "monthly_amount",
            "start_date",
            "end_date",
            "status",
        )


class PaymentResource(resources.ModelResource):
    class Meta:
        model = Payment
        fields = (
            "id",
            "paymentplan",
            "amount_paid",
            "payment_date",
            "payment_method",
            "payment_status",
        )


# ----------------------------
# Admin Classes
# ----------------------------
@admin.register(Bank)
class BankAdmin(ImportExportModelAdmin, ModelAdmin):
    resource_class = BankResource
    list_display = ("bank_name", "bank_abreviation", "account_number", "status")
    list_filter = ("status",)
    search_fields = ("bank_name", "bank_abreviation", "account_number")
    ordering = ("bank_name",)

    actions = ["activate_banks", "deactivate_banks", "suspend_banks"]

    def activate_banks(self, request, queryset):
        """Active les banques sélectionnées"""
        updated = queryset.update(status="active")
        self.message_user(request, f"{updated} banque(s) activée(s).")

    def deactivate_banks(self, request, queryset):
        """Désactive les banques sélectionnées"""
        updated = queryset.update(status="inactive")
        self.message_user(request, f"{updated} banque(s) désactivée(s).")

    def suspend_banks(self, request, queryset):
        """Suspend les banques sélectionnées"""
        updated = queryset.update(status="suspended")
        self.message_user(request, f"{updated} banque(s) suspendue(s).")

    activate_banks.short_description = "Activer les banques sélectionnées"
    deactivate_banks.short_description = "Désactiver les banques sélectionnées"
    suspend_banks.short_description = "Suspendre les banques sélectionnées"


@admin.register(Wording)
class WordingAdmin(ImportExportModelAdmin, ModelAdmin):
    resource_class = WordingResource
    list_display = ("wording_name",)
    search_fields = ("wording_name",)
    ordering = ("wording_name",)


@admin.register(FeesSheet)
class FeesSheetAdmin(ImportExportModelAdmin, ModelAdmin):
    resource_class = FeesSheetResource
    list_display = ("wording", "base_amount", "academic_year", "get_level")
    list_filter = ("academic_year", "wording", "faculty", "department")
    search_fields = (
        "wording__wording_name",
        "class_fk__class_name",
        "department__department_name",
        "faculty__faculty_name",
    )
    ordering = ("-academic_year", "wording")

    def get_level(self, obj):
        if obj.class_fk:
            return f"Classe: {obj.class_fk.class_name}"
        elif obj.department:
            return f"Département: {obj.department.department_name}"
        elif obj.faculty:
            return f"Faculté: {obj.faculty.faculty_name}"
        return "Aucun niveau défini"

    get_level.short_description = "Niveau d'application"


@admin.register(PaymentPlan)
class PaymentPlanAdmin(ImportExportModelAdmin, ModelAdmin):
    resource_class = PaymentPlanResource
    list_display = (
        "feessheet",
        "description",
        "total_amount",
        "monthly_amount",
        "start_date",
        "end_date",
        "status",
    )
    list_filter = ("status", "start_date", "end_date")
    search_fields = ("feessheet__wording__wording_name",)
    ordering = ("-start_date",)


@admin.register(PaymentInstallement)
class PaymentInstallementAdmin(ImportExportModelAdmin, ModelAdmin):
    list_display = (
        "student",
        "amount",
        "paid_amount",
        "due_date",
        "status",
        "payment_plan",
    )
    list_filter = ("status", "due_date", "created_at")
    search_fields = (
        "student__user__first_name",
        "student__user__last_name",
        "student__matricule",
    )
    ordering = ("-due_date",)
    readonly_fields = ("paid_amount", "status", "paid_date")

    actions = ["recalculate_status"]

    def recalculate_status(self, request, queryset):
        """Recalculer le statut des échéanciers sélectionnés"""
        updated = 0
        for installment in queryset:
            installment.save()  # Déclenche la logique de mise à jour du statut
            updated += 1
        self.message_user(request, f"{updated} échéancier(s) mis à jour.")

    recalculate_status.short_description = (
        "Recalculer le statut des échéanciers sélectionnés"
    )


@admin.register(Payment)
class PaymentAdmin(ImportExportModelAdmin, ModelAdmin):
    resource_class = PaymentResource
    list_display = (
        "paymentplan",
        "amount_paid",
        "payment_date",
        "payment_method",
        "payment_status",
        "user",
    )
    list_filter = ("payment_status", "payment_method", "payment_date", "reception_date")
    search_fields = (
        "user__first_name",
        "user__last_name",
        "bank_slip_ref",
        "transaction_code",
    )
    ordering = ("-payment_date",)


@admin.register(PaymentReminder)
class PaymentReminderAdmin(ModelAdmin):
    list_display = (
        "student",
        "reminder_type",
        "amount_due",
        "status",
        "sent_at",
        "sent_by",
    )
    list_filter = ("reminder_type", "status", "sent_at")
    search_fields = (
        "student__user__first_name",
        "student__user__last_name",
        "student__matricule",
    )
    ordering = ("-sent_at",)
    readonly_fields = ("sent_at",)

    fieldsets = (
        (
            "Informations du rappel",
            {"fields": ("student", "reminder_type", "amount_due")},
        ),
        ("Message", {"fields": ("message",)}),
        ("Statut", {"fields": ("status", "sent_by", "sent_at")}),
    )

    actions = ["resend_reminders"]

    def resend_reminders(self, request, queryset):
        """Renvoyer les rappels sélectionnés"""
        from .services import NotificationService

        sent_count = 0
        for reminder in queryset:
            try:
                NotificationService.send_payment_reminder(reminder)
                reminder.status = "sent"
                reminder.save()
                sent_count += 1
            except Exception:
                reminder.status = "failed"
                reminder.save()

        self.message_user(request, f"{sent_count} rappel(s) renvoyé(s) avec succès.")

    resend_reminders.short_description = "Renvoyer les rappels sélectionnés"


@admin.register(PaymentPromise)
class PaymentPromiseAdmin(ModelAdmin):
    list_display = (
        "student",
        "promised_amount",
        "promised_date",
        "status",
        "recorded_at",
    )
    list_filter = ("status", "promised_date", "recorded_at")
    search_fields = (
        "student__user__first_name",
        "student__user__last_name",
        "student__matricule",
    )
    ordering = ("-promised_date",)


@admin.register(CollectionCorrespondence)
class CollectionCorrespondenceAdmin(ModelAdmin):
    list_display = ("student", "correspondence_type", "subject", "sent_at", "sent_by")
    list_filter = ("correspondence_type", "sent_at")
    search_fields = (
        "student__user__first_name",
        "student__user__last_name",
        "student__matricule",
        "subject",
    )
    ordering = ("-sent_at",)
