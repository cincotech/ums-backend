from django.contrib import admin

from .models import PaymentDerogation, RecteurDecision


@admin.register(PaymentDerogation)
class PaymentDerogationAdmin(admin.ModelAdmin):
    list_display = ["student", "derogation_type", "amount", "status", "created_at"]
    list_filter = ["status", "derogation_type", "created_at"]
    search_fields = ["student__user__email", "student__matricule"]
    readonly_fields = ["created_at", "reviewed_at"]


@admin.register(RecteurDecision)
class RecteurDecisionAdmin(admin.ModelAdmin):
    list_display = ["decision_type", "decision", "decided_by", "decided_at"]
    list_filter = ["decision_type", "decision", "decided_at"]
    search_fields = ["reference_id", "decided_by__email"]
    readonly_fields = ["decided_at"]
