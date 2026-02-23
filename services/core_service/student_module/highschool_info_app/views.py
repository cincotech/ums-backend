from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import OrderingFilter, SearchFilter

from core.views import BaseViewSet

from .filters import (
    CertificateFilter,
    HighschoolFilter,
    OptionFilter,
    SectionFilter,
    TrainingCenterFilter,
)
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
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_class = HighschoolFilter
    search_fields = ["hs_name", "code", "zone__zone_name"]
    ordering_fields = ["hs_name", "code", "zone__zone_name", "id"]
    ordering = ["hs_name"]


class SectionViewSet(BaseViewSet):
    queryset = Section.objects.all()
    serializer_class = SectionSerializer
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_class = SectionFilter
    search_fields = ["section_name"]
    ordering_fields = ["section_name", "id"]
    ordering = ["section_name"]


class CertificateViewSet(BaseViewSet):
    queryset = Certificate.objects.all()
    serializer_class = CertificateSerializer
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_class = CertificateFilter
    search_fields = ["certificate_name", "section__section_name"]
    ordering_fields = ["certificate_name", "section__section_name", "id"]
    ordering = ["certificate_name"]


class OptionViewSet(BaseViewSet):
    queryset = Option.objects.all()
    serializer_class = OptionSerializer
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_class = OptionFilter
    search_fields = ["option_name", "section__section_name"]
    ordering_fields = ["option_name", "section__section_name", "id"]
    ordering = ["option_name"]


class TrainingCenterViewSet(BaseViewSet):
    queryset = TrainingCenter.objects.all()
    serializer_class = TrainingCenterSerializer
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_class = TrainingCenterFilter
    search_fields = ["name", "commune__commune_name"]
    ordering_fields = ["name", "commune__commune_name", "id"]
    ordering = ["name"]
