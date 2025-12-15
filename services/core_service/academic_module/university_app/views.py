# Create your views here.
from rest_framework import permissions

from core.views import BaseViewSet

from .models import AcademicYear, University, UniversityDegree
from .serializers import (
    AcademicYearSerializer,
    UniversityDegreeSerializer,
    UniversitySerializer,
)


class AcademicYearViewSet(BaseViewSet):
    queryset = AcademicYear.objects.all()
    serializer_class = AcademicYearSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        qs = AcademicYear.objects.all()
        university_id = self.request.query_params.get("university_id")

        if university_id:
            qs = qs.filter(university_id=university_id)

        return qs

    def perform_create(self, serializer):
        university, created = University.objects.get_or_create(
            university_name="Université Polytechnique de Gitega",
            defaults={"university_abrev": "UPG"},
        )
        serializer.save(university=university)


class UniversityViewSet(BaseViewSet):
    queryset = University.objects.all()
    serializer_class = UniversitySerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        qs = University.objects.all()
        country_id = self.request.query_params.get("country_id")

        if country_id:
            qs = qs.filter(country_id=country_id)

        return qs


class UniversityDegreeViewSet(BaseViewSet):
    queryset = UniversityDegree.objects.all()
    serializer_class = UniversityDegreeSerializer
    permission_classes = [permissions.IsAuthenticated]
