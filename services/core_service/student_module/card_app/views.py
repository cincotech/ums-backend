# Create your views here.
from rest_framework import permissions

from core.views import BaseViewSet
from services.core_service.student_module.card_app.models import (
    StudentCard,
    StudentCardLog,
)

from .serializers import StudentCardLogSerializer, StudentCardSerializer


class StudentCardViewSet(BaseViewSet):
    queryset = StudentCard.objects.all()
    serializer_class = StudentCardSerializer
    permission_classes = [permissions.IsAuthenticated]


class StudentCardLogViewSet(BaseViewSet):
    queryset = StudentCardLog.objects.all()
    serializer_class = StudentCardLogSerializer
    permission_classes = [permissions.IsAuthenticated]
