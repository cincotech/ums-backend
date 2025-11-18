from rest_framework import serializers

from services.core_service.finance_module.payment_app.models import Payment
from services.core_service.student_module.student_profile_app.models import Student

from .models import (
    CollectionCorrespondence,
    LegalCase,
    PaymentInstallment,
    PaymentPlan,
    PaymentPromise,
    PaymentReminder,
)


class DebtorStudentSerializer(serializers.ModelSerializer):
    student_name = serializers.SerializerMethodField()
    total_debt = serializers.DecimalField(max_digits=10, decimal_places=2)
    overdue_amount = serializers.DecimalField(max_digits=10, decimal_places=2)
    days_overdue = serializers.IntegerField()
    program = serializers.SerializerMethodField()

    class Meta:
        model = Student
        fields = [
            "id",
            "matricule",
            "student_name",
            "total_debt",
            "overdue_amount",
            "days_overdue",
            "program",
        ]

    def get_student_name(self, obj):
        return f"{obj.user.first_name} {obj.user.last_name}"

    def get_program(self, obj):
        return (
            obj.graduate_infos.first().department.name
            if obj.graduate_infos.exists()
            else "N/A"
        )


class PaymentInstallmentSerializer(serializers.ModelSerializer):
    student_name = serializers.SerializerMethodField()

    class Meta:
        model = PaymentInstallment
        fields = [
            "id",
            "student",
            "student_name",
            "amount",
            "due_date",
            "status",
            "paid_amount",
            "paid_date",
            "created_at",
        ]
        read_only_fields = ["id", "created_at"]

    def get_student_name(self, obj):
        return f"{obj.student.user.first_name} {obj.student.user.last_name}"


class PaymentReminderSerializer(serializers.ModelSerializer):
    student_name = serializers.SerializerMethodField()

    class Meta:
        model = PaymentReminder
        fields = [
            "id",
            "student",
            "student_name",
            "reminder_type",
            "amount_due",
            "message",
            "status",
            "sent_at",
        ]
        read_only_fields = ["id", "sent_at"]

    def get_student_name(self, obj):
        return f"{obj.student.user.first_name} {obj.student.user.last_name}"


class PaymentPlanSerializer(serializers.ModelSerializer):
    student_name = serializers.SerializerMethodField()

    class Meta:
        model = PaymentPlan
        fields = [
            "id",
            "student",
            "student_name",
            "total_amount",
            "monthly_amount",
            "start_date",
            "end_date",
            "status",
            "created_at",
        ]
        read_only_fields = ["id", "created_at"]

    def get_student_name(self, obj):
        return f"{obj.student.user.first_name} {obj.student.user.last_name}"


class PaymentPromiseSerializer(serializers.ModelSerializer):
    student_name = serializers.SerializerMethodField()

    class Meta:
        model = PaymentPromise
        fields = [
            "id",
            "student",
            "student_name",
            "promised_amount",
            "promised_date",
            "status",
            "notes",
            "recorded_at",
        ]
        read_only_fields = ["id", "recorded_at"]

    def get_student_name(self, obj):
        return f"{obj.student.user.first_name} {obj.student.user.last_name}"


class CollectionCorrespondenceSerializer(serializers.ModelSerializer):
    student_name = serializers.SerializerMethodField()

    class Meta:
        model = CollectionCorrespondence
        fields = [
            "id",
            "student",
            "student_name",
            "correspondence_type",
            "subject",
            "content",
            "response",
            "sent_at",
        ]
        read_only_fields = ["id", "sent_at"]

    def get_student_name(self, obj):
        return f"{obj.student.user.first_name} {obj.student.user.last_name}"


class LegalCaseSerializer(serializers.ModelSerializer):
    student_name = serializers.SerializerMethodField()

    class Meta:
        model = LegalCase
        fields = [
            "id",
            "student",
            "student_name",
            "total_debt",
            "case_documents",
            "status",
            "prepared_at",
        ]
        read_only_fields = ["id", "prepared_at"]

    def get_student_name(self, obj):
        return f"{obj.student.user.first_name} {obj.student.user.last_name}"


class CollectionStatsSerializer(serializers.Serializer):
    total_debtors = serializers.IntegerField()
    total_debt_amount = serializers.DecimalField(max_digits=15, decimal_places=2)
    overdue_cases = serializers.IntegerField()
    active_payment_plans = serializers.IntegerField()
    pending_promises = serializers.IntegerField()
    legal_cases = serializers.IntegerField()


class PaymentRecordSerializer(serializers.ModelSerializer):
    student_name = serializers.SerializerMethodField()

    class Meta:
        model = Payment
        fields = [
            "id",
            "student",
            "student_name",
            "amount_paid",
            "payment_date",
            "payment_method",
            "reference",
        ]
        read_only_fields = ["id", "payment_date"]

    def get_student_name(self, obj):
        return f"{obj.student.user.first_name} {obj.student.user.last_name}"
