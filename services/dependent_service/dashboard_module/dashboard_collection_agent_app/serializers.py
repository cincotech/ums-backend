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


class FeesSheetInfoMixin:
    """Mixin pour les méthodes de sérialisation des informations FeesSheet"""

    def get_wording_info(self, obj):
        wording = getattr(obj, "wording", None)
        if wording:
            return {"id": str(wording.id), "wording_name": wording.wording_name}
        return None

    def get_class_info(self, obj):
        class_fk = getattr(obj, "class_fk", None)
        if class_fk:
            return {
                "id": str(class_fk.id),
                "class_name": class_fk.class_name,
                "department_name": (
                    class_fk.department.department_name if class_fk.department else None
                ),
                "faculty_name": (
                    class_fk.department.faculty.faculty_name
                    if class_fk.department and class_fk.department.faculty
                    else None
                ),
            }
        return None

    def get_department_info(self, obj):
        department = getattr(obj, "department", None)
        if department:
            return {
                "id": str(department.id),
                "department_name": department.department_name,
                "faculty_name": (
                    department.faculty.faculty_name if department.faculty else None
                ),
            }
        return None

    def get_faculty_info(self, obj):
        faculty = getattr(obj, "faculty", None)
        if faculty:
            return {"id": str(faculty.id), "faculty_name": faculty.faculty_name}
        return None

    def get_academic_year_info(self, obj):
        academic_year = getattr(obj, "academic_year", None)
        if academic_year:
            return {
                "id": str(academic_year.id),
                "academic_year": academic_year.academic_year,
            }
        return None


class BankSerializer(serializers.ModelSerializer):
    class Meta:
        model = Bank
        fields = ["id", "bank_name", "bank_abreviation"]


class WordingSerializer(serializers.ModelSerializer):
    class Meta:
        model = Wording
        fields = ["id", "wording_name"]


class FeesSheetSerializer(FeesSheetInfoMixin, serializers.ModelSerializer):
    wording_info = serializers.SerializerMethodField()
    class_info = serializers.SerializerMethodField()
    department_info = serializers.SerializerMethodField()
    faculty_info = serializers.SerializerMethodField()
    academic_year_info = serializers.SerializerMethodField()

    class Meta:
        model = FeesSheet
        fields = [
            "id",
            "class_fk",
            "class_info",
            "department",
            "department_info",
            "faculty",
            "faculty_info",
            "academic_year",
            "academic_year_info",
            "wording",
            "wording_info",
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


class PaymentPlanSerializer(FeesSheetInfoMixin, serializers.ModelSerializer):
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
                "base_amount": obj.feessheet.base_amount,
                "wording": self.get_wording_info(obj.feessheet),
                "class_fk": self.get_class_info(obj.feessheet),
                "department": self.get_department_info(obj.feessheet),
                "faculty": self.get_faculty_info(obj.feessheet),
                "academic_year": self.get_academic_year_info(obj.feessheet),
            }
        return None


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
