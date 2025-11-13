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


class UniversityViewSet(BaseViewSet):
    queryset = University.objects.all()
    serializer_class = UniversitySerializer
    permission_classes = [permissions.IsAuthenticated]


class UniversityDegreeViewSet(BaseViewSet):
    queryset = UniversityDegree.objects.all()
    serializer_class = UniversityDegreeSerializer
    permission_classes = [permissions.IsAuthenticated]
