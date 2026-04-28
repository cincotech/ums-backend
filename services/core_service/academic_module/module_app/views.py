from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import OrderingFilter, SearchFilter

from core.views import BaseViewSet

from .filters import ModuleFilter
from .models import Module, Semester
from .serializers import ModuleSerializer, SemesterSerializer


class ModuleViewSet(BaseViewSet):
    queryset = Module.objects.all()
    serializer_class = ModuleSerializer
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_class = ModuleFilter
    search_fields = ["module_name", "code", "class_fk__class_name"]
    ordering_fields = ["module_name"]
    ordering = ["module_name"]


class SemesterViewSet(BaseViewSet):
    queryset = Semester.objects.all()
    serializer_class = SemesterSerializer
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    search_fields = ["name", "number"]
    ordering_fields = ["number", "name"]
    ordering = ["number"]
