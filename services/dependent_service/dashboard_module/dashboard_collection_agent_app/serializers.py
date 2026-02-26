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
        fields = ["id", "bank_name", "bank_abreviation", "account_number", "status"]


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
        # Récupérer les valeurs des niveaux depuis les données ou l'instance existante
        class_fk = data.get("class_fk")
        department = data.get("department")
        faculty = data.get("faculty")

        # Pour les mises à jour (PUT/PATCH), récupérer les valeurs existantes si non fournies
        if self.instance:
            # Utiliser les valeurs existantes si elles ne sont pas dans les données
            if "class_fk" not in data:
                class_fk = self.instance.class_fk
            if "department" not in data:
                department = self.instance.department
            if "faculty" not in data:
                faculty = self.instance.faculty

        # Vérifier qu'exactement un seul niveau est défini seulement si au moins un niveau est mentionné
        level_fields_in_data = any(
            field in data for field in ["class_fk", "department", "faculty"]
        )

        if level_fields_in_data or not self.instance:
            # Compter les niveaux définis
            levels_set = sum([bool(class_fk), bool(department), bool(faculty)])

            if levels_set == 0:
                raise serializers.ValidationError(
                    "Vous devez définir exactement un niveau : classe, département ou faculté."
                )
            elif levels_set > 1:
                raise serializers.ValidationError(
                    "Vous ne pouvez définir qu'un seul niveau à la fois : classe, département ou faculté."
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
            "description",
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
    student_matricule = serializers.SerializerMethodField()
    payment_plan_info = serializers.SerializerMethodField()
    remaining_amount = serializers.SerializerMethodField()
    completion_percentage = serializers.SerializerMethodField()
    status_display = serializers.SerializerMethodField()
    is_overdue = serializers.SerializerMethodField()
    days_overdue = serializers.SerializerMethodField()

    class Meta:
        model = PaymentInstallement
        fields = [
            "id",
            "payment_plan",
            "payment_plan_info",
            "student",
            "student_name",
            "student_matricule",
            "amount",
            "paid_amount",
            "remaining_amount",
            "completion_percentage",
            "due_date",
            "status",
            "status_display",
            "is_overdue",
            "days_overdue",
            "paid_date",
            "created_by",
            "created_at",
        ]
        read_only_fields = ["paid_amount", "paid_date", "status", "amount"]

    def get_student_name(self, obj):
        return f"{obj.student.user.first_name} {obj.student.user.last_name}"

    def get_student_matricule(self, obj):
        return obj.student.matricule

    def get_remaining_amount(self, obj):
        return obj.amount - obj.paid_amount

    def get_completion_percentage(self, obj):
        if obj.amount > 0:
            return round((obj.paid_amount / obj.amount) * 100, 2)
        return 0

    def get_status_display(self, obj):
        return obj.get_status_display()

    def get_is_overdue(self, obj):
        return obj.status == "overdue"

    def get_days_overdue(self, obj):
        if obj.status == "overdue":
            from django.utils import timezone

            return (timezone.now().date() - obj.due_date).days
        return 0

    def get_payment_plan_info(self, obj):
        return {
            "id": str(obj.payment_plan.id),
            "total_amount": obj.payment_plan.total_amount,
            "monthly_amount": obj.payment_plan.monthly_amount,
            "start_date": obj.payment_plan.start_date,
            "end_date": obj.payment_plan.end_date,
            "status": obj.payment_plan.status,
            "wording": (
                obj.payment_plan.feessheet.wording.wording_name
                if obj.payment_plan.feessheet
                else None
            ),
        }


class PaymentSerializer(serializers.ModelSerializer):
    inscription = serializers.UUIDField(
        required=False, allow_null=True, write_only=True
    )
    remittance_slip = serializers.ImageField(
        required=False, allow_null=True, source="remittance_slip_uri"
    )
    paymentplan_info = serializers.SerializerMethodField()
    bank_info = serializers.SerializerMethodField()
    verified_by_info = serializers.SerializerMethodField()
    inscription_info = serializers.SerializerMethodField()
    user_info = serializers.SerializerMethodField()
    paymentplan = serializers.UUIDField(write_only=True)
    bank = serializers.UUIDField(write_only=True)

    class Meta:
        model = Payment
        fields = [
            "id",
            "paymentplan",
            "paymentplan_info",
            "amount_paid",
            "payment_date",
            "reception_date",
            "payment_method",
            "bank",
            "bank_info",
            "transaction_code",
            "inscription",
            "inscription_info",
            "user",
            "user_info",
            "description",
            "remittance_slip",
            "payment_status",
            "verified_by",
            "verified_by_info",
            "verified_at",
        ]
        read_only_fields = ["user", "verified_by", "verified_at"]

    def get_paymentplan_info(self, obj):
        if obj.paymentplan:
            return {
                "id": str(obj.paymentplan.id),
                "description": obj.paymentplan.description,
                "total_amount": obj.paymentplan.total_amount,
                "monthly_amount": obj.paymentplan.monthly_amount,
                "start_date": obj.paymentplan.start_date,
                "end_date": obj.paymentplan.end_date,
                "status": obj.paymentplan.status,
                "wording_name": (
                    obj.paymentplan.feessheet.wording.wording_name
                    if obj.paymentplan.feessheet and obj.paymentplan.feessheet.wording
                    else None
                ),
            }
        return None

    def get_bank_info(self, obj):
        if obj.bank:
            return {
                "id": str(obj.bank.id),
                "bank_name": obj.bank.bank_name,
                "bank_abreviation": obj.bank.bank_abreviation,
                "account_number": obj.bank.account_number,
                "status": obj.bank.status,
            }
        return None

    def get_verified_by_info(self, obj):
        if obj.verified_by:
            return {
                "id": str(obj.verified_by.id),
                "first_name": obj.verified_by.first_name,
                "last_name": obj.verified_by.last_name,
                "email": obj.verified_by.email,
                "role": obj.verified_by.role.name if obj.verified_by.role else None,
            }
        return None

    def get_inscription_info(self, obj):
        if obj.inscription:
            return {
                "id": str(obj.inscription.id),
                "regist_status": obj.inscription.regist_status,
                "date_inscription": (
                    obj.inscription.date_inscription.isoformat()
                    if obj.inscription.date_inscription
                    else None
                ),
                "student": {
                    "id": str(obj.inscription.student.id),
                    "matricule": obj.inscription.student.matricule,
                    "first_name": obj.inscription.student.user.first_name,
                    "last_name": obj.inscription.student.user.last_name,
                    "email": obj.inscription.student.user.email,
                },
                "class_fk": (
                    {
                        "id": str(obj.inscription.class_fk.id),
                        "class_name": obj.inscription.class_fk.class_name,
                        "department": (
                            obj.inscription.class_fk.department.department_name
                            if obj.inscription.class_fk.department
                            else None
                        ),
                    }
                    if obj.inscription.class_fk
                    else None
                ),
                "academic_year": (
                    {
                        "id": str(obj.inscription.academic_year.id),
                        "academic_year": obj.inscription.academic_year.academic_year,
                    }
                    if obj.inscription.academic_year
                    else None
                ),
            }
        return None

    def get_user_info(self, obj):
        if obj.user:
            return {
                "id": str(obj.user.id),
                "first_name": obj.user.first_name,
                "last_name": obj.user.last_name,
                "email": obj.user.email,
                "role": obj.user.role.name if obj.user.role else None,
            }
        return None

    def validate_inscription(self, value):
        if value == "" or value == "<uuid-inscription>" or value is None:
            return None

        # Convertir l'UUID en instance d'Inscription
        from services.core_service.student_module.inscription_app.models import (
            Inscription,
        )

        try:
            return Inscription.objects.get(id=value)
        except Inscription.DoesNotExist:
            raise serializers.ValidationError("Inscription non trouvée.")

    def validate_paymentplan(self, value):
        if value is None:
            return None

        try:
            return PaymentPlan.objects.get(id=value)
        except PaymentPlan.DoesNotExist:
            raise serializers.ValidationError("Plan de paiement non trouvé.")

    def validate_bank(self, value):
        if value is None:
            return None

        try:
            return Bank.objects.get(id=value)
        except Bank.DoesNotExist:
            raise serializers.ValidationError("Banque non trouvée.")

    def to_internal_value(self, data):
        # Debug: afficher les données reçues
        print(f"DEBUG PaymentSerializer - données reçues: {data}")
        print(
            f"DEBUG PaymentSerializer - clés: {list(data.keys()) if hasattr(data, 'keys') else 'N/A'}"
        )

        # Ne pas modifier les données du fichier
        if "inscription" in data and (
            data["inscription"] == "" or data["inscription"] == "<uuid-inscription>"
        ):
            data = data.copy()
            data["inscription"] = None
        return super().to_internal_value(data)

    def validate(self, data):
        # Validation minimale - laisser _handle_surplus gérer la redistribution
        return data

    def create(self, validated_data):
        from services.core_service.student_module.inscription_app.models import (
            Inscription,
        )
        from services.core_service.student_module.student_profile_app.models import (
            Student,
        )

        user = self.context["request"].user
        user_role = user.role.name
        validated_data["user"] = user

        # inscription est déjà un objet après validate_inscription
        inscription = validated_data.get("inscription")

        if user_role in ["student", "guest"]:
            try:
                student = Student.objects.get(user=user)
                # Si pas d'inscription fournie, prendre l'inscription Active en priorité
                if not inscription:
                    # D'abord chercher une inscription Active
                    inscription = (
                        Inscription.objects.filter(
                            student=student, regist_status="Active"
                        )
                        .order_by("-date_inscription")
                        .first()
                    )

                    # Si pas d'Active, chercher une Pending
                    if not inscription:
                        inscription = (
                            Inscription.objects.filter(
                                student=student, regist_status="Pending"
                            )
                            .order_by("-date_inscription")
                            .first()
                        )

                    if inscription:
                        validated_data["inscription"] = inscription
                    else:
                        raise serializers.ValidationError(
                            "Aucune inscription active ou en attente trouvée pour cet étudiant."
                        )
            except Student.DoesNotExist:
                raise serializers.ValidationError("Profil étudiant non trouvé.")

        # Créer l'instance en passant l'utilisateur actuel
        payment = Payment(**validated_data)
        payment.save(_current_user=user)
        return payment

    def update(self, instance, validated_data):
        user = self.context["request"].user

        # Mettre à jour les champs
        for attr, value in validated_data.items():
            setattr(instance, attr, value)

        # Le modèle Payment appellera automatiquement PaymentService si nécessaire
        instance.save(_current_user=user)
        return instance


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
