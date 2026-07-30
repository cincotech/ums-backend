from typing import ClassVar

from django_filters.rest_framework import DjangoFilterBackend

from core.views import BaseViewSet
from services.search.backends import TypesenseFilterBackend, TypesenseOrderingFilter

from .filters import TeacherFilter
from .models import Attribution, Suggestion, Teacher
from .serializers import AttributionSerializer, SuggestionSerializer, TeacherSerializer


class TeacherViewSet(BaseViewSet):
    queryset = Teacher.objects.all()
    serializer_class = TeacherSerializer
    filter_backends: ClassVar[list] = [
        TypesenseFilterBackend,
        DjangoFilterBackend,
        TypesenseOrderingFilter,
    ]
    filterset_class = TeacherFilter
    search_fields: ClassVar[list] = [
        "user__first_name",
        "user__last_name",
        "user__email",
        "teacher_grade",
        "speciality",
    ]
    filter_fields: ClassVar[list] = ["faculty_id", "university_id", "department_id"]
    ordering_fields: ClassVar[list] = [
        "user__first_name",
        "user__last_name",
        "teacher_grade",
    ]
    ordering: ClassVar[list] = ["user__last_name"]


class AttributionViewSet(BaseViewSet):
    queryset = Attribution.objects.all()
    serializer_class = AttributionSerializer


class SuggestionViewSet(BaseViewSet):
    queryset = Suggestion.objects.all()
    serializer_class = SuggestionSerializer
