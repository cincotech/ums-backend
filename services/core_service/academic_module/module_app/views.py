from django_filters.rest_framework import DjangoFilterBackend

from core.views import BaseViewSet
from services.search.backends import TypesenseFilterBackend, TypesenseOrderingFilter

from .filters import ModuleFilter
from .models import Module, Semester
from .serializers import ModuleSerializer, SemesterSerializer


class ModuleViewSet(BaseViewSet):
    queryset = Module.objects.all()
    serializer_class = ModuleSerializer
    filter_backends = [
        TypesenseFilterBackend,
        DjangoFilterBackend,
        TypesenseOrderingFilter,
    ]
    filterset_class = ModuleFilter
    search_fields = ["module_name", "code", "class_fk__class_name"]
    filter_fields = ["faculty_id", "university_id", "department_id"]
    ordering_fields = ["module_name"]
    ordering = ["module_name"]


class SemesterViewSet(BaseViewSet):
    queryset = Semester.objects.all()
    serializer_class = SemesterSerializer
    filter_backends = [
        TypesenseFilterBackend,
        DjangoFilterBackend,
        TypesenseOrderingFilter,
    ]
    search_fields = ["name", "number"]
    filter_fields = ["faculty_id", "university_id"]
    ordering_fields = ["number", "name"]
    ordering = ["number"]
