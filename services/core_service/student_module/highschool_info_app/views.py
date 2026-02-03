# Create your views here.

from core.views import BaseViewSet

from .models import Certificate, Highschool, Option, Section, TrainingCenter
from .serializers import (
    CertificateSerializer,
    HighschoolSerializer,
    OptionSerializer,
    SectionSerializer,
    TrainingCenterSerializer,
)


class HighschoolViewSet(BaseViewSet):
    queryset = Highschool.objects.all()
    serializer_class = HighschoolSerializer
    ordering = ["id"]


class SectionViewSet(BaseViewSet):
    queryset = Section.objects.all()
    serializer_class = SectionSerializer
    ordering = ["id"]


class CertificateViewSet(BaseViewSet):
    queryset = Certificate.objects.all()
    serializer_class = CertificateSerializer
    ordering = ["id"]


class OptionViewSet(BaseViewSet):
    queryset = Option.objects.all()
    serializer_class = OptionSerializer
    ordering = ["id"]


class TrainingCenterViewSet(BaseViewSet):
    queryset = TrainingCenter.objects.all()
    serializer_class = TrainingCenterSerializer
    ordering = ["id"]
