import django_filters
from django.db.models import Q

from .models import AcademicYear, University, UniversityDegree


class UniversityFilter(django_filters.FilterSet):
    search = django_filters.CharFilter(method="filter_search")

    class Meta:
        model = University
        fields = []

    def filter_search(self, queryset, name, value):
        return queryset.filter(
            Q(university_name__icontains=value) | Q(university_code__icontains=value)
        )


class AcademicYearFilter(django_filters.FilterSet):
    search = django_filters.CharFilter(method="filter_search")

    class Meta:
        model = AcademicYear
        fields = []

    def filter_search(self, queryset, name, value):
        return queryset.filter(
            Q(academic_year__icontains=value) | Q(civil_year__icontains=value)
        )


class UniversityDegreeFilter(django_filters.FilterSet):
    search = django_filters.CharFilter(method="filter_search")

    class Meta:
        model = UniversityDegree
        fields = []

    def filter_search(self, queryset, name, value):
        return queryset.filter(Q(degree_name__icontains=value))
