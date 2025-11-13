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


class SectionViewSet(BaseViewSet):
    queryset = Section.objects.all()
    serializer_class = SectionSerializer


class CertificateViewSet(BaseViewSet):
    queryset = Certificate.objects.all()
    serializer_class = CertificateSerializer


class OptionViewSet(BaseViewSet):
    queryset = Option.objects.all()
    serializer_class = OptionSerializer


class TrainingCenterViewSet(BaseViewSet):
    queryset = TrainingCenter.objects.all()
    serializer_class = TrainingCenterSerializer
