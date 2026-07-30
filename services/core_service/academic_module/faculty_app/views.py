from django_filters.rest_framework import DjangoFilterBackend

from core.views import BaseViewSet
from services.search.backends import TypesenseFilterBackend, TypesenseOrderingFilter

from .filters import FacultyFilter, TypeFormationFilter
from .models import Faculty, TypeFormation
from .serializers import FacultySerializer, TypeFormationSerializer


class TypeFormationViewSet(BaseViewSet):
    queryset = TypeFormation.objects.all()
    serializer_class = TypeFormationSerializer
    filter_backends = [
        TypesenseFilterBackend,
        DjangoFilterBackend,
        TypesenseOrderingFilter,
    ]
    filterset_class = TypeFormationFilter
    search_fields = ["name"]
    filter_fields = ["university_id"]
    ordering_fields = ["name"]
    ordering = ["name"]


class FacultyViewSet(BaseViewSet):
    queryset = Faculty.objects.all()
    serializer_class = FacultySerializer
    filter_backends = [
        TypesenseFilterBackend,
        DjangoFilterBackend,
        TypesenseOrderingFilter,
    ]
    filterset_class = FacultyFilter
    search_fields = ["faculty_name", "faculty_abreviation"]
    filter_fields = ["university_id"]
    ordering_fields = ["faculty_name"]
    ordering = ["faculty_name"]

    def get_queryset(self):
        qs = Faculty.objects.all()
        university_id = self.request.query_params.get("university_id")

        if university_id:
            qs = qs.filter(university_id=university_id)

        return qs
