# Create your views here.
from rest_framework import permissions

from core.views import BaseViewSet
from services.core_service.finance_module.concellation_app.models import (
    DebtCancellation,
)

from .serializers import DebtCancellationSerializer


class DebtCancellationViewSet(BaseViewSet):
    queryset = DebtCancellation.objects.all()
    serializer_class = DebtCancellationSerializer
    permission_classes = [permissions.IsAuthenticated]
