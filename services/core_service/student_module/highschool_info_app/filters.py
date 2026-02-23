import django_filters
from django.db.models import Q

from .models import Certificate, Highschool, Option, Section, TrainingCenter


class HighschoolFilter(django_filters.FilterSet):
    search = django_filters.CharFilter(method="filter_search")
    zone = django_filters.UUIDFilter(field_name="zone__id", lookup_expr="exact")
    zone_name = django_filters.CharFilter(
        field_name="zone__zone_name", lookup_expr="icontains"
    )
    code = django_filters.CharFilter(field_name="code", lookup_expr="icontains")

    class Meta:
        model = Highschool
        fields = []

    def filter_search(self, queryset, name, value):
        return queryset.filter(
            Q(hs_name__icontains=value)
            | Q(code__icontains=value)
            | Q(zone__zone_name__icontains=value)
        )


class SectionFilter(django_filters.FilterSet):
    search = django_filters.CharFilter(method="filter_search")

    class Meta:
        model = Section
        fields = []

    def filter_search(self, queryset, name, value):
        return queryset.filter(Q(section_name__icontains=value))


class CertificateFilter(django_filters.FilterSet):
    search = django_filters.CharFilter(method="filter_search")
    section = django_filters.UUIDFilter(field_name="section__id", lookup_expr="exact")
    section_name = django_filters.CharFilter(
        field_name="section__section_name", lookup_expr="icontains"
    )

    class Meta:
        model = Certificate
        fields = []

    def filter_search(self, queryset, name, value):
        return queryset.filter(
            Q(certificate_name__icontains=value)
            | Q(section__section_name__icontains=value)
        )


class OptionFilter(django_filters.FilterSet):
    search = django_filters.CharFilter(method="filter_search")
    section = django_filters.UUIDFilter(field_name="section__id", lookup_expr="exact")
    section_name = django_filters.CharFilter(
        field_name="section__section_name", lookup_expr="icontains"
    )

    class Meta:
        model = Option
        fields = []

    def filter_search(self, queryset, name, value):
        return queryset.filter(
            Q(option_name__icontains=value) | Q(section__section_name__icontains=value)
        )


class TrainingCenterFilter(django_filters.FilterSet):
    search = django_filters.CharFilter(method="filter_search")
    commune = django_filters.UUIDFilter(field_name="commune__id", lookup_expr="exact")
    commune_name = django_filters.CharFilter(
        field_name="commune__commune_name", lookup_expr="icontains"
    )

    class Meta:
        model = TrainingCenter
        fields = []

    def filter_search(self, queryset, name, value):
        return queryset.filter(
            Q(name__icontains=value) | Q(commune__commune_name__icontains=value)
        )
