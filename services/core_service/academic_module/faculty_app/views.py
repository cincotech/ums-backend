from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import OrderingFilter, SearchFilter

from core.views import BaseViewSet

from .filters import FacultyFilter, TypeFormationFilter
from .models import Faculty, TypeFormation
from .serializers import FacultySerializer, TypeFormationSerializer


class TypeFormationViewSet(BaseViewSet):
    queryset = TypeFormation.objects.all()
    serializer_class = TypeFormationSerializer
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_class = TypeFormationFilter
    search_fields = ["name"]
    ordering_fields = ["name"]
    ordering = ["name"]


class FacultyViewSet(BaseViewSet):
    queryset = Faculty.objects.all()
    serializer_class = FacultySerializer
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_class = FacultyFilter
    search_fields = ["faculty_name", "abreviation", "faculty_abreviation"]
    ordering_fields = ["faculty_name"]
    ordering = ["faculty_name"]

    def get_queryset(self):
        qs = Faculty.objects.all()
        university_id = self.request.query_params.get("university_id")

        if university_id:
            qs = qs.filter(university_id=university_id)

        return qs
