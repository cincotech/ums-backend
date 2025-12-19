import uuid

from django.db import models
from django.db.models import Sum

from services.core_service.academic_module.class_app.models import Class
from services.core_service.academic_module.department_app.models import Department
from services.core_service.academic_module.faculty_app.models import Faculty
from services.core_service.academic_module.university_app.models import AcademicYear

# from services.core_service.finance_module.fees_app.models import FeesSheet
from services.core_service.student_module.inscription_app.models import Inscription
from services.core_service.student_module.student_profile_app.models import Student
from services.foundational_service.auth_module.user_app.models import User


class Bank(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    bank_name = models.CharField(max_length=255)
    bank_abreviation = models.CharField(max_length=10)

    class Meta:
        db_table = "banks"


class Wording(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    wording_name = models.CharField(max_length=60)

    class Meta:
        db_table = "wordings"


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
        from django.utils import timezone

        today = timezone.now().date()

        # Mettre à jour le statut automatiquement
        if self.paid_amount >= self.amount and self.status != "paid":
            self.status = "paid"
            if not self.paid_date:
                self.paid_date = today
        elif self.paid_amount < self.amount:
            if self.status == "paid":
                self.status = "pending"
                self.paid_date = None
            # Vérifier si en retard
            elif self.due_date < today and self.status != "overdue":
                self.status = "overdue"

        super().save(*args, **kwargs)


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
    amount_paid = models.PositiveIntegerField()
    payment_date = models.DateField(null=True, blank=True)
    reception_date = models.DateField(null=True, blank=True)
    payment_method = models.CharField(max_length=20, choices=METHOD)
    bank = models.ForeignKey(
        Bank, on_delete=models.RESTRICT, null=True, related_name="bank"
    )
    bank_slip_ref = models.CharField(max_length=128, null=True)
    transaction_code = models.CharField(max_length=50, null=True)
    inscription = models.ForeignKey(
        Inscription,
        on_delete=models.RESTRICT,
        related_name="payments_inscription",
    )
    user = models.ForeignKey(
        User, on_delete=models.RESTRICT, related_name="payments_user"
    )
    description = models.CharField(max_length=250, null=True)
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
        # Récupérer l'ancien montant avant la sauvegarde
        old_amount = 0
        old_status = None
        if self.pk:
            # Utiliser only() pour ne récupérer que les champs nécessaires
            try:
                old_payment = Payment.objects.only("amount_paid", "payment_status").get(
                    pk=self.pk
                )
                old_amount = (
                    old_payment.amount_paid
                    if old_payment.payment_status == "verified"
                    else 0
                )
                old_status = old_payment.payment_status
            except Payment.DoesNotExist:
                pass

        super().save(*args, **kwargs)

        # Ne mettre à jour que si le statut ou le montant a changé
        if (old_status != self.payment_status) or (old_amount != self.amount_paid):
            self._update_payment_installment(old_amount)

    def _update_payment_installment(self, old_amount=0):
        """Met à jour le PaymentInstallement correspondant"""
        if self.payment_status == "verified":
            student = self.inscription.student if self.inscription else None
            if not student:
                return

            # Chercher ou créer PaymentInstallement pour ce plan et cet étudiant
            installment, created = PaymentInstallement.objects.get_or_create(
                payment_plan=self.paymentplan,
                student=student,
                defaults={
                    "amount": self.paymentplan.total_amount,
                    "due_date": self.paymentplan.end_date,
                    "created_by": self.user,
                },
            )

            # Calculer la différence et ajuster le montant payé
            difference = self.amount_paid - old_amount
            installment.paid_amount += difference

            # S'assurer que le montant payé ne devient pas négatif
            if installment.paid_amount < 0:
                installment.paid_amount = 0

            installment.save()

    def can_pay_plan(self, student, target_plan):
        """Vérifie si l'étudiant peut payer ce plan (plans précédents payés)"""
        previous_unpaid = PaymentInstallement.objects.filter(
            student=student,
            payment_plan__start_date__lt=target_plan.start_date,
            status__in=["pending", "overdue"],
        ).exists()

        return not previous_unpaid

    def delete(self, *args, **kwargs):
        """Met à jour le PaymentInstallement après suppression du paiement"""
        super().delete(*args, **kwargs)
        # Recalculer les montants pour tous les PaymentInstallement affectés
        self._recalculate_installments_for_plan()

    def _recalculate_installments_for_plan(self):
        """Recalcule tous les PaymentInstallement pour ce plan de paiement"""
        installments = PaymentInstallement.objects.filter(payment_plan=self.paymentplan)
        for installment in installments:
            total_verified = (
                Payment.objects.filter(
                    paymentplan=self.paymentplan,
                    payment_status="verified",
                    user=(
                        installment.student.user
                        if hasattr(installment.student, "user")
                        else None
                    ),
                ).aggregate(total=Sum("amount_paid"))["total"]
                or 0
            )
            installment.paid_amount = total_verified
            installment.save()


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
