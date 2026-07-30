import django_filters
from django.db.models import Q

from services.search.filterset import TypesenseSearchFilterSet

from .models import AcademicYear, University, UniversityDegree


class UniversityFilter(TypesenseSearchFilterSet):
    search = django_filters.CharFilter(method="filter_search")

    class Meta:
        model = University
        fields = []

    def _orm_filter_search(self, queryset, value):
        return queryset.filter(
            Q(university_name__icontains=value) | Q(university_abrev__icontains=value)
        )


class AcademicYearFilter(TypesenseSearchFilterSet):
    search = django_filters.CharFilter(method="filter_search")

    class Meta:
        model = AcademicYear
        fields = []

    def _orm_filter_search(self, queryset, value):
        return queryset.filter(
            Q(academic_year__icontains=value) | Q(civil_year__icontains=value)
        )


class UniversityDegreeFilter(TypesenseSearchFilterSet):
    search = django_filters.CharFilter(method="filter_search")

    class Meta:
        model = UniversityDegree
        fields = []

    def _orm_filter_search(self, queryset, value):
        return queryset.filter(Q(degree_name__icontains=value))
