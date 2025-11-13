# Create your views here.
from rest_framework import permissions

from core.views import BaseViewSet
from services.core_service.finance_module.fees_app.models import FeesSheet, Wording

from .serializers import FeesSheetSerializer, WordingSerializer


class WordingViewSet(BaseViewSet):
    queryset = Wording.objects.all()
    serializer_class = WordingSerializer
    permission_classes = [permissions.IsAuthenticated]


class FeesSheetViewSet(BaseViewSet):
    queryset = FeesSheet.objects.all()
    serializer_class = FeesSheetSerializer
    permission_classes = [permissions.IsAuthenticated]
