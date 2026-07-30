import django_filters
from django.db.models import Q

from services.search.filterset import TypesenseSearchFilterSet

from .models import Faculty, TypeFormation


class FacultyFilter(TypesenseSearchFilterSet):
    search = django_filters.CharFilter(method="filter_search")

    class Meta:
        model = Faculty
        fields = []

    def _orm_filter_search(self, queryset, value):
        return queryset.filter(
            Q(faculty_name__icontains=value) | Q(faculty_abreviation__icontains=value)
        )


class TypeFormationFilter(TypesenseSearchFilterSet):
    search = django_filters.CharFilter(method="filter_search")

    class Meta:
        model = TypeFormation
        fields = []

    def _orm_filter_search(self, queryset, value):
        return queryset.filter(Q(name__icontains=value))
