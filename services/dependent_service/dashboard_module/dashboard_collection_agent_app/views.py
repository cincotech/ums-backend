from django.contrib.auth import get_user_model
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import OrderingFilter, SearchFilter

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
    queryset = FeesSheet.objects.all()
    serializer_class = FeesSheetSerializer
    permission_classes = [IsFinanceService]
    filter_backends = [DjangoFilterBackend, OrderingFilter]
    filterset_fields = ["class_fk", "academic_year", "wording"]
    ordering_fields = ["base_amount"]


class PaymentInstallementViewSet(BaseViewSet):
    queryset = PaymentInstallement.objects.all()
    serializer_class = PaymentInstallementSerializer
    permission_classes = [IsFinanceService]
    filter_backends = [DjangoFilterBackend, OrderingFilter]
    filterset_fields = ["student", "status", "due_date"]
    ordering_fields = ["due_date", "amount"]


class PaymentReminderViewSet(BaseViewSet):
    queryset = PaymentReminder.objects.all()
    serializer_class = PaymentReminderSerializer
    permission_classes = [IsFinanceService]
    filter_backends = [DjangoFilterBackend, OrderingFilter]
    filterset_fields = ["student", "reminder_type", "status"]
    ordering_fields = ["sent_at"]


class PaymentPlanViewSet(BaseViewSet):
    queryset = PaymentPlan.objects.all()
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
