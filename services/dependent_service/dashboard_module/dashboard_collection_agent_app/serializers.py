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
    class_name = serializers.CharField(source="class_fk.class_name", read_only=True)
    department_name = serializers.CharField(
        source="department.department_name", read_only=True
    )
    faculty_name = serializers.CharField(source="faculty.faculty_name", read_only=True)
    academic_year_name = serializers.CharField(
        source="academic_year.year_name", read_only=True
    )
    wording_name = serializers.CharField(source="wording.wording_name", read_only=True)

    class Meta:
        model = FeesSheet
        fields = [
            "id",
            "class_fk",
            "class_name",
            "department",
            "department_name",
            "faculty",
            "faculty_name",
            "academic_year",
            "academic_year_name",
            "wording",
            "wording_name",
            "base_amount",
        ]

    def validate(self, data):
        class_fk = data.get("class_fk")
        department = data.get("department")
        faculty = data.get("faculty")

        # Vérifier qu'au moins un niveau est défini
        levels_set = sum([bool(class_fk), bool(department), bool(faculty)])

        if levels_set == 0:
            raise serializers.ValidationError(
                "Vous devez définir au moins un niveau : classe, département ou faculté."
            )

        return data


class PaymentInstallementSerializer(serializers.ModelSerializer):
    student_name = serializers.SerializerMethodField()
    payment_plan_info = serializers.SerializerMethodField()

    class Meta:
        model = PaymentInstallement
        fields = [
            "id",
            "payment_plan",
            "payment_plan_info",
            "student",
            "student_name",
            "amount",
            "due_date",
            "status",
            "paid_amount",
            "paid_date",
            "created_by",
            "created_at",
        ]
        read_only_fields = ["paid_amount", "paid_date", "status", "amount"]

    def validate(self, data):
        payment_plan = data.get("payment_plan")

        # Vérifier que payment_plan est défini
        if not payment_plan:
            raise serializers.ValidationError(
                "Le plan de paiement (payment_plan) est requis."
            )

        return data

    def get_student_name(self, obj):
        return f"{obj.student.user.first_name} {obj.student.user.last_name}"

    def get_payment_plan_info(self, obj):
        return {
            "id": str(obj.payment_plan.id),
            "total_amount": obj.payment_plan.total_amount,
            "monthly_amount": obj.payment_plan.monthly_amount,
            "status": obj.payment_plan.status,
            "feessheet_info": (
                {
                    "wording": (
                        obj.payment_plan.feessheet.wording.wording_name
                        if obj.payment_plan.feessheet
                        else None
                    ),
                }
                if obj.payment_plan.feessheet
                else None
            ),
        }


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
    feessheet_info = serializers.SerializerMethodField()

    class Meta:
        model = PaymentPlan
        fields = [
            "id",
            "feessheet",
            "feessheet_info",
            "total_amount",
            "monthly_amount",
            "start_date",
            "end_date",
            "status",
            "created_by",
            "created_at",
        ]
        read_only_fields = ["created_by", "created_at"]

    def get_feessheet_info(self, obj):
        if obj.feessheet:
            return {
                "id": str(obj.feessheet.id),
                "wording": obj.feessheet.wording.wording_name,
                "base_amount": obj.feessheet.base_amount,
            }
        return None


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
    inscription = serializers.UUIDField(required=False, allow_null=True)
    remittance_slip_uri = serializers.ImageField(required=False, allow_null=True)

    def validate_inscription(self, value):
        if value == "" or value == "<uuid-inscription>" or value is None:
            return None
        return value

    def to_internal_value(self, data):
        if "inscription" in data and (
            data["inscription"] == "" or data["inscription"] == "<uuid-inscription>"
        ):
            data = data.copy()
            data["inscription"] = None
        return super().to_internal_value(data)

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
        read_only_fields = ["user"]


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
