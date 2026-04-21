import uuid

from django.db import models

from services.core_service.academic_module.class_app.models import Class
from services.core_service.academic_module.department_app.models import Department
from services.core_service.academic_module.faculty_app.models import Faculty
from services.core_service.academic_module.university_app.models import AcademicYear

# from services.core_service.finance_module.fees_app.models import FeesSheet
from services.core_service.student_module.inscription_app.models import Inscription
from services.core_service.student_module.student_profile_app.models import Student
from services.foundational_service.auth_module.user_app.models import User


class Bank(models.Model):
    STATUS_CHOICES = (
        ("active", "Actif"),
        ("inactive", "Inactif"),
        ("suspended", "Suspendu"),
        ("closed", "Fermé"),
    )

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    bank_name = models.CharField(max_length=255)
    bank_abreviation = models.CharField(max_length=10)
    account_number = models.CharField(max_length=50, null=True, blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="active")

    class Meta:
        db_table = "banks"

    def __str__(self):
        return f"{self.bank_name} ({self.get_status_display()})"

    def activate(self):
        """Active la banque"""
        self.status = "active"
        self.save()

    def deactivate(self):
        """Désactive la banque"""
        self.status = "inactive"
        self.save()

    def suspend(self):
        """Suspend la banque"""
        self.status = "suspended"
        self.save()

    def close(self):
        """Ferme la banque"""
        self.status = "closed"
        self.save()

    @property
    def is_active(self):
        """Vérifie si la banque est active"""
        return self.status == "active"


class Wording(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    wording_name = models.CharField(max_length=60)

    class Meta:
        db_table = "wordings"

    def __str__(self):
        return self.wording_name


class FeesSheet(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    class_fk = models.ForeignKey(
        Class,
        on_delete=models.RESTRICT,
        related_name="fees_sheets_class",
        null=True,
        blank=True,
    )
    department = models.ForeignKey(
        Department,
        on_delete=models.RESTRICT,
        related_name="fees_sheets_department",
        null=True,
        blank=True,
    )
    faculty = models.ForeignKey(
        Faculty,
        on_delete=models.RESTRICT,
        related_name="fees_sheets_faculty",
        null=True,
        blank=True,
    )
    academic_year = models.ForeignKey(
        AcademicYear, on_delete=models.CASCADE, related_name="fees_sheets_academicyear"
    )
    wording = models.ForeignKey(
        Wording, on_delete=models.RESTRICT, related_name="fees_sheets_wording"
    )
    base_amount = models.PositiveIntegerField()

    class Meta:
        db_table = "fees_sheets"

    def clean(self):
        from django.core.exceptions import ValidationError

        # Vérifier qu'exactement un seul niveau est défini
        levels_set = sum(
            [bool(self.class_fk), bool(self.department), bool(self.faculty)]
        )

        if levels_set == 0:
            raise ValidationError(
                "Vous devez définir exactement un niveau : classe, département ou faculté."
            )
        elif levels_set > 1:
            raise ValidationError(
                "Vous ne pouvez définir qu'un seul niveau à la fois : classe, département ou faculté."
            )

    def save(self, *args, **kwargs):
        self.clean()
        super().save(*args, **kwargs)

    def __str__(self):
        if self.class_fk:
            return f"Frais {self.wording.wording_name} - {self.class_fk.class_name}"
        elif self.department:
            return (
                f"Frais {self.wording.wording_name} - {self.department.department_name}"
            )
        elif self.faculty:
            return f"Frais {self.wording.wording_name} - {self.faculty.faculty_name}"
        return f"Frais {self.wording.wording_name}"


class PaymentPlan(models.Model):
    STATUS_CHOICES = (
        ("active", "Actif"),
        ("completed", "Terminé"),
        ("defaulted", "En Défaut"),
        ("cancelled", "Annulé"),
    )

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    feessheet = models.ForeignKey(
        FeesSheet,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="paymentplan_feessheet",
    )
    description = models.CharField(
        max_length=100,
        help_text="Description du plan (ex: Première tranche, Deuxième tranche, etc.)",
        null=True,
        blank=True,
    )
    total_amount = models.DecimalField(max_digits=10, decimal_places=2)
    monthly_amount = models.DecimalField(
        max_digits=10, null=True, blank=True, decimal_places=2
    )
    start_date = models.DateField()
    end_date = models.DateField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="active")
    created_by = models.ForeignKey(User, on_delete=models.RESTRICT)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "payment_plans"

    @classmethod
    def get_plans_for_student(cls, student):
        """Retourne les plans de paiement applicables à un étudiant avec recherche hiérarchique"""
        # Récupérer l'inscription active avec relations préchargées
        active_inscription = (
            student.inscriptions.select_related("class_fk__department__faculty")
            .filter(regist_status__in=["Active", "Pending"])
            .order_by("-date_inscription")
            .first()
        )

        if not active_inscription or not active_inscription.class_fk:
            return cls.objects.none()

        student_class = active_inscription.class_fk
        student_department = student_class.department
        student_faculty = student_department.faculty if student_department else None

        # Base queryset avec relations préchargées
        base_queryset = cls.objects.select_related(
            "feessheet__wording",
            "feessheet__class_fk",
            "feessheet__department",
            "feessheet__faculty",
        ).filter(status="active")

        # Filtrer par année académique de l'inscription active
        if active_inscription.academic_year:
            base_queryset = base_queryset.filter(
                feessheet__academic_year=active_inscription.academic_year
            )

        # 1. D'abord chercher les plans pour SA CLASSE
        class_plans = base_queryset.filter(feessheet__class_fk=student_class)
        if class_plans.exists():
            return class_plans

        # 2. Si pas de plans pour la classe, chercher pour SON DÉPARTEMENT
        if student_department:
            department_plans = base_queryset.filter(
                feessheet__department=student_department
            )
            if department_plans.exists():
                return department_plans

        # 3. Si pas de plans pour le département, chercher pour SA FACULTÉ
        if student_faculty:
            faculty_plans = base_queryset.filter(feessheet__faculty=student_faculty)
            if faculty_plans.exists():
                return faculty_plans

        # 4. Aucun plan trouvé
        return cls.objects.none()

    @classmethod
    def get_plans_for_user(cls, user):
        """Retourne les plans selon le rôle de l'utilisateur"""
        if user.role.name in ["student", "guest"]:
            # Étudiant voit seulement les plans de sa classe/département/faculté
            try:
                student = Student.objects.get(user=user)
                return cls.get_plans_for_student(student)
            except Student.DoesNotExist:
                return cls.objects.none()
        else:
            # Tous les autres rôles (finance, admin, etc.) voient tous les plans
            return cls.objects.all()

    def __str__(self):
        base_str = ""
        if self.feessheet:
            base_str = (
                f"Plan {self.feessheet.wording.wording_name} - {self.total_amount}"
            )
        else:
            base_str = f"Plan de paiement - {self.total_amount}"

        # Ajouter la description si elle existe
        if self.description:
            base_str += f" ({self.description})"

        return base_str


class PaymentInstallement(models.Model):
    STATUS_CHOICES = (
        ("pending", "En Attente"),
        ("paid", "Payé"),
        ("overdue", "En Retard"),
        ("deferred", "Reporté"),
    )

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    payment_plan = models.ForeignKey(
        PaymentPlan,
        on_delete=models.CASCADE,
        related_name="installments",
        null=True,
        blank=True,
    )
    student = models.ForeignKey(Student, on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    due_date = models.DateField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="pending")
    paid_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    paid_date = models.DateField(null=True, blank=True)
    created_by = models.ForeignKey(User, on_delete=models.RESTRICT)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "payment_installments"

    def save(self, *args, **kwargs):
        import logging

        from django.utils import timezone

        logger = logging.getLogger(__name__)
        today = timezone.now().date()

        # Détecter si le montant a changé
        is_new = self.pk is None
        old_amount = None
        if not is_new:
            try:
                old_inst = PaymentInstallement.objects.only("amount").get(pk=self.pk)
                old_amount = old_inst.amount
            except PaymentInstallement.DoesNotExist:
                pass

        # Mettre à jour le statut automatiquement
        if self.paid_amount >= self.amount:
            self.status = "paid"
            if not self.paid_date:
                self.paid_date = today
        elif self.paid_amount < self.amount:
            self.paid_date = None
            if self.due_date < today:
                self.status = "overdue"
            else:
                self.status = "pending"

        super().save(*args, **kwargs)

        # Si le montant a changé, recalculer via PaymentService
        if old_amount is not None and old_amount != self.amount:
            logger.info(
                "\n🔔 Modèle PaymentInstallement - Changement de montant détecté"
            )
            logger.info(f"   Ancien: {old_amount} → Nouveau: {self.amount}")
            logger.info("📞 Appel de PaymentService pour recalculer les surplus")

            from django.db.models import Sum

            from .services import PaymentService

            # Recalculer le total vérifié pour ce plan
            total_verified = (
                Payment.objects.filter(
                    paymentplan=self.payment_plan,
                    payment_status="verified",
                    inscription__student=self.student,
                ).aggregate(total=Sum("amount_paid"))["total"]
                or 0
            )

            # Ajuster paid_amount si nécessaire
            self.paid_amount = min(total_verified, self.amount)
            PaymentInstallement.objects.filter(pk=self.pk).update(
                paid_amount=self.paid_amount
            )

            # Gérer le surplus si nécessaire
            surplus = max(total_verified - self.amount, 0)
            if surplus > 0:
                logger.info(f"💸 Surplus détecté après modification: {surplus}")
                # Récupérer le dernier paiement pour obtenir les infos nécessaires
                last_payment = (
                    Payment.objects.filter(
                        paymentplan=self.payment_plan,
                        payment_status="verified",
                        inscription__student=self.student,
                    )
                    .order_by("-verified_at")
                    .first()
                )

                if last_payment:
                    PaymentService._handle_surplus(
                        self.student,
                        self.payment_plan,
                        surplus,
                        last_payment.payment_method,
                        last_payment.bank,
                        last_payment.transaction_code,
                    )


class Payment(models.Model):
    METHOD = (
        ("bank_deposit", "Bank Deposit"),
        ("bank_transfert", "Bank Transfer"),
        ("bank_check", "Bank Check"),
        ("mobile_money", "Mobile Money"),
        ("other", "Other"),
    )
    STATUS = (
        ("verified", "Verified"),
        ("unverified", "Unverified"),
        ("rejected", "Rejected"),
    )
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    paymentplan = models.ForeignKey(
        PaymentPlan, on_delete=models.RESTRICT, related_name="payments_paymentplan"
    )
    amount_paid = models.DecimalField(max_digits=10, decimal_places=2)
    payment_date = models.DateField(null=True, blank=True)
    reception_date = models.DateField(null=True, blank=True)
    payment_method = models.CharField(max_length=20, choices=METHOD)
    bank = models.ForeignKey(
        Bank, on_delete=models.RESTRICT, null=True, related_name="bank"
    )
    transaction_code = models.CharField(max_length=50, null=True, blank=True)
    inscription = models.ForeignKey(
        Inscription,
        on_delete=models.RESTRICT,
        related_name="payments_inscription",
    )
    user = models.ForeignKey(
        User, on_delete=models.RESTRICT, related_name="payments_user"
    )
    description = models.CharField(max_length=250, null=True, blank=True)
    remittance_slip_uri = models.ImageField(
        upload_to="payment_slips/", null=True, blank=True
    )
    payment_status = models.CharField(
        max_length=20, choices=STATUS, default="unverified"
    )
    verified_by = models.ForeignKey(
        User,
        on_delete=models.RESTRICT,
        null=True,
        blank=True,
        related_name="verified_payments",
    )
    verified_at = models.DateTimeField(null=True, blank=True)
    # history = HistoricalRecords()

    class Meta:
        db_table = "payments"

    @classmethod
    def get_payments_for_user(cls, user):
        """Retourne les paiements selon le rôle de l'utilisateur"""
        if user.role.name == "finance_service":
            # Finance voit tous les paiements
            return cls.objects.all()
        elif user.role.name == "student":
            # Étudiant voit seulement ses paiements
            return cls.objects.filter(inscription__student__user=user)
        else:
            # Autres rôles n'ont pas accès
            return cls.objects.none()

    @classmethod
    def create_payment(cls, created_by_user, **payment_data):
        """Crée un paiement - tout le monde peut créer, statut unverified par défaut"""
        payment_data["user"] = created_by_user
        payment_data["payment_status"] = (
            "unverified"  # Toujours unverified à la création
        )
        return cls.objects.create(**payment_data)

    def verify(self, verified_by_user):
        """Valide le paiement par le service financier"""
        from django.utils import timezone

        if verified_by_user.role.name != "finance_service":
            raise ValueError("Seul le service financier peut valider les paiements.")

        self.payment_status = "verified"
        self.verified_by = verified_by_user
        self.verified_at = timezone.now()
        self.save()

    def save(self, *args, **kwargs):
        import logging

        from django.utils import timezone

        logger = logging.getLogger(__name__)

        skip_surplus = kwargs.pop("_skip_surplus_handling", False)
        current_user = kwargs.pop("_current_user", None)

        is_new = self.pk is None
        old_status = None
        old_amount = None
        old_paymentplan = None

        if not is_new:
            try:
                old_payment = Payment.objects.only(
                    "payment_status", "amount_paid", "paymentplan"
                ).get(pk=self.pk)
                old_status = old_payment.payment_status
                old_amount = old_payment.amount_paid
                old_paymentplan = old_payment.paymentplan

                # Vérifier si le statut a changé et que ce n'est pas le service financier
                if old_status != self.payment_status and current_user:
                    if current_user.role.name != "finance_service":
                        raise ValueError(
                            "Seul le service financier peut modifier le statut des paiements."
                        )
            except Payment.DoesNotExist:
                pass

        if self.payment_status == "verified" and not self.verified_by and current_user:
            self.verified_by = current_user
        if self.payment_status == "verified" and not self.verified_at:
            self.verified_at = timezone.now()

        super().save(*args, **kwargs)

        # Appeler PaymentService après la sauvegarde si nécessaire
        if not skip_surplus:
            from django.db.models import Sum

            from .services import PaymentService

            student = self.inscription.student if self.inscription else None
            if not student:
                return

            # 1. Changement de statut vers "verified"
            if old_status != "verified" and self.payment_status == "verified":
                logger.info(f"\n🔔 Payment - Vérification du paiement {self.id}")
                logger.info("📞 Appel de PaymentService pour gérer les surplus")

                installment, _ = PaymentInstallement.objects.get_or_create(
                    student=student,
                    payment_plan=self.paymentplan,
                    defaults={
                        "amount": self.paymentplan.total_amount,
                        "due_date": self.paymentplan.end_date,
                        "created_by": self.user,
                    },
                )

                total_verified = (
                    Payment.objects.filter(
                        paymentplan=self.paymentplan,
                        payment_status="verified",
                        inscription__student=student,
                    ).aggregate(total=Sum("amount_paid"))["total"]
                    or 0
                )

                installment.paid_amount = min(total_verified, installment.amount)
                installment.save()

                surplus = max(total_verified - installment.amount, 0)
                if surplus > 0:
                    logger.info(f"💸 Surplus détecté: {surplus}")
                    PaymentService._handle_surplus(
                        student,
                        self.paymentplan,
                        surplus,
                        self.payment_method,
                        self.bank,
                        self.transaction_code,
                    )

            # 2. Changement de statut de "verified" vers "unverified/rejected"
            elif old_status == "verified" and self.payment_status in [
                "unverified",
                "rejected",
            ]:
                logger.info(f"\n❌ Payment - Rejet du paiement {self.id}")
                logger.info("📞 Recalcul de tous les installments")

                auto_payments = Payment.objects.filter(
                    inscription__student=student,
                    payment_status="verified",
                    description__icontains="Surplus",
                ) | Payment.objects.filter(
                    inscription__student=student,
                    payment_status="verified",
                    description__icontains="Redistribution",
                )

                count = auto_payments.count()
                if count > 0:
                    logger.info(f"🗑️ Suppression de {count} paiements automatiques")
                    auto_payments.delete()

                logger.info("📊 Recalcul des installments...")
                for inst in PaymentInstallement.objects.filter(
                    student=student
                ).order_by("payment_plan__start_date"):
                    total_verified = (
                        Payment.objects.filter(
                            paymentplan=inst.payment_plan,
                            payment_status="verified",
                            inscription__student=student,
                        ).aggregate(total=Sum("amount_paid"))["total"]
                        or 0
                    )
                    inst.paid_amount = total_verified
                    inst.save()
                    logger.info(
                        f"  - {inst.payment_plan.description}: {total_verified}"
                    )

            # 3. Modification du montant (paiement vérifié)
            elif (
                self.payment_status == "verified"
                and old_amount is not None
                and old_amount != self.amount_paid
            ):
                logger.info("\n🔔 Payment - Changement de montant détecté")
                logger.info(f"   Ancien: {old_amount} → Nouveau: {self.amount_paid}")
                logger.info("📞 Recalcul des installments et surplus")

                installment = PaymentInstallement.objects.filter(
                    student=student, payment_plan=self.paymentplan
                ).first()

                if installment:
                    total_verified = (
                        Payment.objects.filter(
                            paymentplan=self.paymentplan,
                            payment_status="verified",
                            inscription__student=student,
                        ).aggregate(total=Sum("amount_paid"))["total"]
                        or 0
                    )

                    installment.paid_amount = min(total_verified, installment.amount)
                    installment.save()

                    surplus = max(total_verified - installment.amount, 0)
                    if surplus > 0:
                        logger.info(f"💸 Surplus détecté: {surplus}")
                        PaymentService._handle_surplus(
                            student,
                            self.paymentplan,
                            surplus,
                            self.payment_method,
                            self.bank,
                            self.transaction_code,
                        )

            # 4. Changement de plan de paiement (paiement vérifié)
            elif (
                self.payment_status == "verified"
                and old_paymentplan is not None
                and old_paymentplan != self.paymentplan
            ):
                logger.info("\n🔔 Payment - Changement de plan détecté")
                logger.info(
                    f"   Ancien: {old_paymentplan.description} → Nouveau: {self.paymentplan.description}"
                )
                logger.info("📞 Recalcul des deux plans")

                # Recalculer l'ancien plan
                old_inst = PaymentInstallement.objects.filter(
                    student=student, payment_plan=old_paymentplan
                ).first()
                if old_inst:
                    old_total = (
                        Payment.objects.filter(
                            paymentplan=old_paymentplan,
                            payment_status="verified",
                            inscription__student=student,
                        ).aggregate(total=Sum("amount_paid"))["total"]
                        or 0
                    )
                    old_inst.paid_amount = old_total
                    old_inst.save()

                # Recalculer le nouveau plan
                new_inst, _ = PaymentInstallement.objects.get_or_create(
                    student=student,
                    payment_plan=self.paymentplan,
                    defaults={
                        "amount": self.paymentplan.total_amount,
                        "due_date": self.paymentplan.end_date,
                        "created_by": self.user,
                    },
                )
                new_total = (
                    Payment.objects.filter(
                        paymentplan=self.paymentplan,
                        payment_status="verified",
                        inscription__student=student,
                    ).aggregate(total=Sum("amount_paid"))["total"]
                    or 0
                )
                new_inst.paid_amount = min(new_total, new_inst.amount)
                new_inst.save()

                surplus = max(new_total - new_inst.amount, 0)
                if surplus > 0:
                    logger.info(f"💸 Surplus détecté: {surplus}")
                    PaymentService._handle_surplus(
                        student,
                        self.paymentplan,
                        surplus,
                        self.payment_method,
                        self.bank,
                        self.transaction_code,
                    )


class PaymentReminder(models.Model):
    REMINDER_TYPES = (
        ("reminder_7", "Rappel J+7"),
        ("reminder_30", "Relance J+30"),
        ("formal_notice_60", "Mise en Demeure J+60"),
        ("final_notice", "Dernier Avis"),
    )

    STATUS_CHOICES = (
        ("sent", "Envoyé"),
        ("delivered", "Livré"),
        ("failed", "Échec"),
        ("pending", "En Attente"),
    )

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    student = models.ForeignKey(Student, on_delete=models.CASCADE)
    reminder_type = models.CharField(max_length=50, choices=REMINDER_TYPES)
    amount_due = models.DecimalField(max_digits=10, decimal_places=2)
    message = models.TextField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="pending")
    sent_by = models.ForeignKey(User, on_delete=models.RESTRICT)
    sent_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "payment_reminders"


class PaymentPromise(models.Model):
    STATUS_CHOICES = (
        ("pending", "En Attente"),
        ("kept", "Respecté"),
        ("broken", "Non Respecté"),
    )

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    student = models.ForeignKey(Student, on_delete=models.CASCADE)
    promised_amount = models.DecimalField(max_digits=10, decimal_places=2)
    promised_date = models.DateField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="pending")
    notes = models.TextField(null=True, blank=True)
    recorded_by = models.ForeignKey(User, on_delete=models.RESTRICT)
    recorded_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "payment_promises"


class CollectionCorrespondence(models.Model):
    CORRESPONDENCE_TYPES = (
        ("email", "Email"),
        ("sms", "SMS"),
        ("letter", "Courrier"),
        ("phone", "Téléphone"),
        ("meeting", "Rencontre"),
    )

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    student = models.ForeignKey(Student, on_delete=models.CASCADE)
    correspondence_type = models.CharField(max_length=20, choices=CORRESPONDENCE_TYPES)
    subject = models.CharField(max_length=255)
    content = models.TextField()
    response = models.TextField(null=True, blank=True)
    sent_by = models.ForeignKey(User, on_delete=models.RESTRICT)
    sent_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "collection_correspondence"
