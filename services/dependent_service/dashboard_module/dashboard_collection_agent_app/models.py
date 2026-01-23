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
        from django.utils import timezone

        today = timezone.now().date()

        # Mettre à jour le statut automatiquement
        if self.paid_amount >= self.amount:
            self.status = "paid"
            if not self.paid_date:
                self.paid_date = today
        elif self.paid_amount < self.amount:
            # Si le montant n'est pas totalisé, réinitialiser la date de paiement
            self.paid_date = None
            # Vérifier si en retard
            if self.due_date < today:
                self.status = "overdue"
            else:
                self.status = "pending"

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
        """Crée un paiement - finance_service, student ou student_service peuvent créer"""
        if created_by_user.role.name not in [
            "finance_service",
            "student",
            "student_service",
        ]:
            raise ValueError(
                "Seuls le service financier, les étudiants et le service aux étudiants peuvent créer les paiements."
            )

        payment_data["user"] = created_by_user
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
        # Vérifier si l'étudiant peut créer un nouveau paiement
        if not self.pk:  # Seulement pour les nouveaux paiements
            if self.inscription:
                student = self.inscription.student

                # Vérifier s'il y a des PaymentInstallement non payés pour d'AUTRES plans (antérieurs)
                other_unpaid_installments = (
                    PaymentInstallement.objects.filter(
                        student=student,
                        status__in=["pending", "overdue"],
                        payment_plan__start_date__lt=self.paymentplan.start_date,  # Plans antérieurs seulement
                    )
                    .exclude(payment_plan=self.paymentplan)  # Exclure le plan actuel
                    .exists()
                )

                if other_unpaid_installments:
                    raise ValueError(
                        f"Impossible de créer ce paiement. L'étudiant {student.user.get_full_name()} ({student.matricule}) doit d'abord terminer les plans de paiement précédents."
                    )

        # Récupérer l'ancien montant avant la sauvegarde
        old_amount = 0
        old_status = None
        if self.pk:
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

        # Mettre à jour le PaymentInstallement si le statut est vérifié
        if self.payment_status == "verified" or old_status == "verified":
            self._update_payment_installment(old_amount)

    def _update_payment_installment(self, old_amount=0):
        """Met à jour le PaymentInstallement correspondant"""
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

        # Recalculer le montant total payé pour ce plan et cet étudiant
        total_verified_payments = (
            Payment.objects.filter(
                paymentplan=self.paymentplan,
                payment_status="verified",
                inscription__student=student,
            ).aggregate(total=Sum("amount_paid"))["total"]
            or 0
        )

        installment.paid_amount = total_verified_payments
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
                    inscription__student=installment.student,
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
