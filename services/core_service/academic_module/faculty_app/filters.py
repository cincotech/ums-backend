import django_filters
from django.db.models import Q

from .models import Faculty, TypeFormation


class FacultyFilter(django_filters.FilterSet):
    search = django_filters.CharFilter(method="filter_search")

    class Meta:
        model = Faculty
        fields = []

    def filter_search(self, queryset, name, value):
        return queryset.filter(
            Q(faculty_name__icontains=value) | Q(faculty_abreviation__icontains=value)
            )


class TypeFormationFilter(django_filters.FilterSet):
    search = django_filters.CharFilter(method="filter_search")

    class Meta:
        model = TypeFormation
        fields = []

    def filter_search(self, queryset, name, value):
        return queryset.filter(Q(name__icontains=value))
