from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import OrderingFilter, SearchFilter

from core.views import BaseViewSet

from .filters import ModuleFilter
from .models import Module
from .serializers import ModuleSerializer


class ModuleViewSet(BaseViewSet):
    queryset = Module.objects.all()
    serializer_class = ModuleSerializer
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_class = ModuleFilter
    search_fields = ["module_name", "module_code", "class_fk__class_name"]
    ordering_fields = ["module_name"]
    ordering = ["module_name"]
