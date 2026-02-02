from django.db.models import Q
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import OrderingFilter, SearchFilter
from rest_framework.permissions import IsAuthenticated

from core.views import BaseViewSet

from .models import CompiledResult, Result, Session, Supplement
from .serializers import (
    CompiledResultSerializer,
    ResultSerializer,
    SessionSerializer,
    SupplementSerializer,
)


class SessionViewSet(BaseViewSet):
    queryset = Session.objects.all()
    serializer_class = SessionSerializer
    permission_classes = [IsAuthenticated]


class ResultViewSet(BaseViewSet):
    queryset = Result.objects.all()
    serializer_class = ResultSerializer
    permission_classes = [IsAuthenticated]


class CompiledResultViewSet(BaseViewSet):
    queryset = CompiledResult.objects.all()
    serializer_class = CompiledResultSerializer
    permission_classes = [IsAuthenticated]


class SupplementViewSet(BaseViewSet):
    queryset = Supplement.objects.all()
    serializer_class = SupplementSerializer
    permission_classes = [IsAuthenticated]
