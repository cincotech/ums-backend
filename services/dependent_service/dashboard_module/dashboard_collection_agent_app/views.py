from django.contrib.auth import get_user_model
from django.utils import timezone
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.decorators import action
from rest_framework.filters import OrderingFilter, SearchFilter
from rest_framework.response import Response

from core.permissions import IsFinanceService, IsStudent, IsStudentOrFinanceService
from core.views import BaseViewSet

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
from .serializers import (
    BankSerializer,
    CollectionCorrespondenceSerializer,
    FeesSheetSerializer,
    PaymentInstallementSerializer,
    PaymentPlanSerializer,
    PaymentPromiseSerializer,
    PaymentReminderSerializer,
    PaymentSerializer,
    WordingSerializer,
)

User = get_user_model()


class BankViewSet(BaseViewSet):
    queryset = Bank.objects.all()
    serializer_class = BankSerializer
    permission_classes = [IsFinanceService]
    filter_backends = [SearchFilter]
    search_fields = ["bank_name", "bank_abreviation"]


class WordingViewSet(BaseViewSet):
    queryset = Wording.objects.all()
    serializer_class = WordingSerializer
    permission_classes = [IsFinanceService]
    filter_backends = [SearchFilter]
    search_fields = ["wording_name"]


class FeesSheetViewSet(BaseViewSet):
    queryset = FeesSheet.objects.select_related(
        "class_fk",
        "class_fk__department",
        "class_fk__department__faculty",
        "department",
        "department__faculty",
        "faculty",
        "academic_year",
        "wording",
    ).all()
    serializer_class = FeesSheetSerializer
    permission_classes = [IsFinanceService]
    filter_backends = [DjangoFilterBackend, OrderingFilter]
    filterset_fields = [
        "class_fk",
        "department",
        "faculty",
        "academic_year",
        "wording",
    ]
    ordering_fields = ["base_amount"]


class PaymentInstallementViewSet(BaseViewSet):
    queryset = (
        PaymentInstallement.objects.select_related(
            "student__user",
            "payment_plan__feessheet__wording",
            "payment_plan__feessheet__academic_year",
        )
        .prefetch_related(
            "student__inscriptions__class_fk__department__faculty",
            "student__inscriptions__academic_year",
        )
        .all()
    )
    serializer_class = PaymentInstallementSerializer
    permission_classes = [IsStudentOrFinanceService]
    filter_backends = [DjangoFilterBackend, OrderingFilter]
    filterset_fields = ["payment_plan", "student", "status", "due_date"]
    ordering_fields = ["due_date", "amount"]

    def get_queryset(self):
        """Filtre les échéanciers selon le rôle de l'utilisateur"""
        user = self.request.user
        if user.role.name == "finance_service":
            return self.queryset
        elif user.role.name == "student":
            # Étudiant voit seulement ses échéanciers
            return self.queryset.filter(student__user=user)
        return PaymentInstallement.objects.none()

    def list(self, request, *args, **kwargs):
        """Liste optimisée avec données organisées"""
        queryset = self.filter_queryset(self.get_queryset())
        page = self.paginate_queryset(queryset)

        if page is not None:
            data = self._format_installments_data(page)
            return self.get_paginated_response(data)

        data = self._format_installments_data(queryset)
        return Response(data)

    def _format_installments_data(self, installments):
        """Formate les données pour l'affichage"""
        data = []

        for inst in installments:
            # Récupérer l'inscription active
            active_inscription = inst.student.inscriptions.filter(
                regist_status="Active"
            ).first()

            data.append(
                {
                    "id": str(inst.id),
                    "student": {
                        "id": str(inst.student.id),
                        "name": f"{inst.student.user.first_name} {inst.student.user.last_name}",
                        "matricule": inst.student.matricule,
                    },
                    "class_info": (
                        {
                            "id": (
                                str(active_inscription.class_fk.id)
                                if active_inscription and active_inscription.class_fk
                                else None
                            ),
                            "name": (
                                active_inscription.class_fk.class_name
                                if active_inscription and active_inscription.class_fk
                                else None
                            ),
                            "department": (
                                active_inscription.class_fk.department.department_name
                                if active_inscription
                                and active_inscription.class_fk
                                and active_inscription.class_fk.department
                                else None
                            ),
                            "faculty": (
                                active_inscription.class_fk.department.faculty.faculty_name
                                if active_inscription
                                and active_inscription.class_fk
                                and active_inscription.class_fk.department
                                and active_inscription.class_fk.department.faculty
                                else None
                            ),
                        }
                        if active_inscription
                        else None
                    ),
                    "payment_plan": {
                        "id": str(inst.payment_plan.id),
                        "total_amount": inst.payment_plan.total_amount,
                        "monthly_amount": inst.payment_plan.monthly_amount,
                        "start_date": inst.payment_plan.start_date,
                        "end_date": inst.payment_plan.end_date,
                        "status": inst.payment_plan.status,
                        "wording": (
                            inst.payment_plan.feessheet.wording.wording_name
                            if inst.payment_plan.feessheet
                            else None
                        ),
                    },
                    "financial_info": {
                        "amount": inst.amount,
                        "paid_amount": inst.paid_amount,
                        "remaining_amount": inst.amount - inst.paid_amount,
                        "completion_percentage": (
                            round((inst.paid_amount / inst.amount) * 100, 2)
                            if inst.amount > 0
                            else 0
                        ),
                    },
                    "status_info": {
                        "status": inst.status,
                        "status_display": inst.get_status_display(),
                        "is_overdue": inst.status == "overdue",
                        "days_overdue": (
                            (timezone.now().date() - inst.due_date).days
                            if inst.status == "overdue"
                            else 0
                        ),
                    },
                    "dates": {
                        "due_date": inst.due_date,
                        "paid_date": inst.paid_date,
                        "created_at": inst.created_at,
                    },
                }
            )

        return data

    @action(detail=False, methods=["get"])
    def my_installments(self, request):
        """Échéanciers de l'étudiant connecté"""
        if request.user.role.name != "student":
            return Response({"error": "Accès réservé aux étudiants"}, status=403)

        installments = self.get_queryset().filter(student__user=request.user)
        data = []

        for inst in installments:
            data.append(
                {
                    "id": str(inst.id),
                    "amount": inst.amount,
                    "paid_amount": inst.paid_amount,
                    "remaining_amount": inst.amount - inst.paid_amount,
                    "due_date": inst.due_date,
                    "status": inst.status,
                    "status_display": inst.get_status_display(),
                    "paid_date": inst.paid_date,
                    "is_overdue": inst.status == "overdue",
                    "payment_plan": {
                        "id": str(inst.payment_plan.id),
                        "total_amount": inst.payment_plan.total_amount,
                        "wording": (
                            inst.payment_plan.feessheet.wording.wording_name
                            if inst.payment_plan.feessheet
                            else None
                        ),
                        "start_date": inst.payment_plan.start_date,
                        "end_date": inst.payment_plan.end_date,
                    },
                }
            )

        return Response({"count": len(data), "installments": data})


class PaymentReminderViewSet(BaseViewSet):
    queryset = PaymentReminder.objects.all()
    serializer_class = PaymentReminderSerializer
    permission_classes = [IsFinanceService]
    filter_backends = [DjangoFilterBackend, OrderingFilter]
    filterset_fields = ["student", "reminder_type", "status"]
    ordering_fields = ["sent_at"]


class PaymentPlanViewSet(BaseViewSet):
    queryset = PaymentPlan.objects.select_related(
        "feessheet__wording",
        "feessheet__class_fk",
        "feessheet__class_fk__department",
        "feessheet__class_fk__department__faculty",
        "feessheet__department",
        "feessheet__department__faculty",
        "feessheet__faculty",
        "feessheet__academic_year",
    ).all()
    serializer_class = PaymentPlanSerializer
    permission_classes = [IsFinanceService]
    filter_backends = [DjangoFilterBackend, OrderingFilter]
    filterset_fields = ["feessheet", "status", "created_by"]
    ordering_fields = ["start_date", "total_amount"]

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        from rest_framework import status

        from core.response_handler import success_response, validate_serializer

        validation_error = validate_serializer(serializer)
        if validation_error:
            return validation_error
        serializer.save(created_by=request.user)
        return success_response(
            data=serializer.data,
            message=f"{self.queryset.model.__name__} created successfully",
            status_code=status.HTTP_201_CREATED,
        )


class PaymentPromiseViewSet(BaseViewSet):
    queryset = PaymentPromise.objects.all()
    serializer_class = PaymentPromiseSerializer
    permission_classes = [IsStudent]
    filter_backends = [DjangoFilterBackend, OrderingFilter]
    filterset_fields = ["student", "status", "promised_date"]
    ordering_fields = ["promised_date", "promised_amount"]


class PaymentViewSet(BaseViewSet):
    queryset = Payment.objects.select_related(
        "paymentplan__feessheet__wording",
        "paymentplan__feessheet__academic_year",
        "bank",
        "inscription__student__user",
        "inscription__academic_year",
        "inscription__class_fk",
        "user",
        "verified_by",
    ).all()
    serializer_class = PaymentSerializer
    filter_backends = [DjangoFilterBackend, OrderingFilter]
    filterset_fields = [
        "paymentplan",
        "payment_method",
        "payment_status",
        "bank",
        "inscription",
        "user",
    ]

    ordering_fields = ["payment_date", "amount_paid"]

    def get_permissions(self):
        if self.action in ["update", "partial_update"]:
            return [IsFinanceService()]
        return [IsStudentOrFinanceService()]

    def get_queryset(self):
        """Filtre les paiements selon le rôle de l'utilisateur"""
        return Payment.get_payments_for_user(self.request.user)

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        from rest_framework import status

        from core.response_handler import success_response, validate_serializer

        validation_error = validate_serializer(serializer)
        if validation_error:
            return validation_error
        serializer.save(user=request.user)
        return success_response(
            data=serializer.data,
            message=f"{self.queryset.model.__name__} created successfully",
            status_code=status.HTTP_201_CREATED,
        )


class CollectionCorrespondenceViewSet(BaseViewSet):
    queryset = CollectionCorrespondence.objects.all()
    serializer_class = CollectionCorrespondenceSerializer
    permission_classes = [IsFinanceService]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ["student", "correspondence_type"]
    search_fields = ["subject", "content"]
    ordering_fields = ["sent_at"]
