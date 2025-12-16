from django.contrib.auth import get_user_model
from django.utils import timezone
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.decorators import action
from rest_framework.filters import OrderingFilter, SearchFilter
from rest_framework.response import Response

from core.permissions import IsFinanceService, IsStudent
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
        "class_fk", "department", "faculty", "academic_year", "wording"
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
    queryset = PaymentInstallement.objects.select_related(
        "student__user", "payment_plan__feessheet__wording"
    ).all()
    serializer_class = PaymentInstallementSerializer
    permission_classes = [IsFinanceService]
    filter_backends = [DjangoFilterBackend, OrderingFilter]
    filterset_fields = ["payment_plan", "student", "status", "due_date"]
    ordering_fields = ["due_date", "amount"]

    @action(detail=False, methods=["get"])
    def payment_statistics(self, request):
        """Statistiques des paiements"""
        total = self.queryset.count()
        paid = self.queryset.filter(status="paid").count()
        overdue = self.queryset.filter(status="overdue").count()
        pending = self.queryset.filter(status="pending").count()

        return Response(
            {
                "total_installments": total,
                "paid_count": paid,
                "overdue_count": overdue,
                "pending_count": pending,
                "completion_rate": round((paid / total * 100), 2) if total > 0 else 0,
            }
        )

    @action(detail=False, methods=["get"])
    def completed_students(self, request):
        """Liste des étudiants qui ont terminé leurs paiements"""
        completed = self.queryset.filter(status="paid").select_related("student__user")
        data = [
            {
                "student_id": str(inst.student.id),
                "student_name": f"{inst.student.user.first_name} {inst.student.user.last_name}",
                "matricule": inst.student.matricule,
                "amount_paid": inst.paid_amount,
                "paid_date": inst.paid_date,
                "payment_plan_id": str(inst.payment_plan.id),
            }
            for inst in completed
        ]

        return Response({"count": len(data), "students": data})

    @action(detail=False, methods=["get"])
    def overdue_students(self, request):
        """Liste des étudiants en retard"""
        overdue = self.queryset.filter(status="overdue").select_related("student__user")
        data = [
            {
                "student_id": str(inst.student.id),
                "student_name": f"{inst.student.user.first_name} {inst.student.user.last_name}",
                "matricule": inst.student.matricule,
                "amount_due": inst.amount - inst.paid_amount,
                "due_date": inst.due_date,
                "days_overdue": (timezone.now().date() - inst.due_date).days,
                "payment_plan_id": str(inst.payment_plan.id),
            }
            for inst in overdue
        ]

        return Response({"count": len(data), "students": data})

    @action(detail=False, methods=["get"])
    def students_by_class(self, request):
        """Liste des étudiants par classe et statut de paiement"""
        class_id = request.query_params.get("class_id")
        payment_plan_id = request.query_params.get("payment_plan_id")
        status = request.query_params.get("status", "paid")  # par défaut: terminé
        academic_year_id = request.query_params.get("academic_year_id")

        if not class_id:
            return Response({"error": "class_id is required"}, status=400)

        # Filtrer par classe via l'inscription
        queryset = self.queryset.filter(
            student__inscriptions__class_fk_id=class_id,
            student__inscriptions__regist_status="Active",
            status=status,
        )

        # Filtrer par plan de paiement si spécifié
        if payment_plan_id:
            queryset = queryset.filter(payment_plan_id=payment_plan_id)

        # Filtrer par année académique si spécifié
        if academic_year_id:
            queryset = queryset.filter(
                student__inscriptions__academic_year_id=academic_year_id
            )

        queryset = queryset.select_related(
            "student__user", "payment_plan__feessheet__wording"
        ).distinct()

        data = []
        for inst in queryset:
            # Récupérer l'inscription active de l'étudiant pour cette classe
            inscription = inst.student.inscriptions.filter(
                class_fk_id=class_id, regist_status="Active"
            ).first()

            data.append(
                {
                    "student_id": str(inst.student.id),
                    "student_name": f"{inst.student.user.first_name} {inst.student.user.last_name}",
                    "matricule": inst.student.matricule,
                    "class_name": (
                        inscription.class_fk.class_name if inscription else None
                    ),
                    "academic_year": (
                        inscription.academic_year.year_name if inscription else None
                    ),
                    "payment_status": inst.status,
                    "amount": inst.amount,
                    "paid_amount": inst.paid_amount,
                    "paid_date": inst.paid_date,
                    "due_date": inst.due_date,
                    "payment_plan_info": {
                        "id": str(inst.payment_plan.id),
                        "total_amount": inst.payment_plan.total_amount,
                        "wording": (
                            inst.payment_plan.feessheet.wording.wording_name
                            if inst.payment_plan.feessheet
                            else None
                        ),
                    },
                }
            )

        return Response(
            {
                "count": len(data),
                "class_id": class_id,
                "status_filter": status,
                "students": data,
            }
        )


class PaymentReminderViewSet(BaseViewSet):
    queryset = PaymentReminder.objects.all()
    serializer_class = PaymentReminderSerializer
    permission_classes = [IsFinanceService]
    filter_backends = [DjangoFilterBackend, OrderingFilter]
    filterset_fields = ["student", "reminder_type", "status"]
    ordering_fields = ["sent_at"]


class PaymentPlanViewSet(BaseViewSet):
    queryset = PaymentPlan.objects.select_related("feessheet__wording").all()
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
    queryset = Payment.objects.all()
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
        return [IsStudent()]

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
