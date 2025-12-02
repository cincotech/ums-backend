from rest_framework import serializers

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


class BankSerializer(serializers.ModelSerializer):
    class Meta:
        model = Bank
        fields = ["id", "bank_name", "bank_abreviation"]


class WordingSerializer(serializers.ModelSerializer):
    class Meta:
        model = Wording
        fields = ["id", "wording_name"]


class FeesSheetSerializer(serializers.ModelSerializer):
    class Meta:
        model = FeesSheet
        fields = [
            "id",
            "class_fk",
            "academic_year",
            "wording",
            "base_amount",
            "installements",
        ]


class PaymentInstallementSerializer(serializers.ModelSerializer):
    class Meta:
        model = PaymentInstallement
        fields = [
            "id",
            "student",
            "amount",
            "due_date",
            "status",
            "paid_amount",
            "paid_date",
            "created_by",
            "created_at",
        ]


class PaymentReminderSerializer(serializers.ModelSerializer):
    class Meta:
        model = PaymentReminder
        fields = [
            "id",
            "student",
            "reminder_type",
            "amount_due",
            "message",
            "status",
            "sent_by",
            "sent_at",
        ]


class PaymentPlanSerializer(serializers.ModelSerializer):
    class Meta:
        model = PaymentPlan
        fields = [
            "id",
            "feessheet",
            "total_amount",
            "monthly_amount",
            "start_date",
            "end_date",
            "status",
            "created_by",
            "created_at",
        ]


class PaymentPromiseSerializer(serializers.ModelSerializer):
    class Meta:
        model = PaymentPromise
        fields = [
            "id",
            "student",
            "promised_amount",
            "promised_date",
            "status",
            "notes",
            "recorded_by",
            "recorded_at",
        ]


class PaymentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Payment
        fields = [
            "id",
            "paymentplan",
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
        ]


class CollectionCorrespondenceSerializer(serializers.ModelSerializer):
    class Meta:
        model = CollectionCorrespondence
        fields = [
            "id",
            "student",
            "correspondence_type",
            "subject",
            "content",
            "response",
            "sent_by",
            "sent_at",
        ]
