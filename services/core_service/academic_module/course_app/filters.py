import django_filters
from django.db.models import Q

from services.search.filterset import TypesenseSearchFilterSet

from .models import Course, Module


class CourseFilter(TypesenseSearchFilterSet):
    # Full-text search via Typesense or ORM fallback
    search = django_filters.CharFilter(method="filter_search")

    # Filtres relationnels
    module = django_filters.ModelChoiceFilter(
        field_name="module",
        to_field_name="id",
        queryset=Module.objects.all(),
        label="Module",
    )

    class Meta:
        model = Course
        fields = ["module"]

    def filter_queryset(self, queryset):
        return super().filter_queryset(queryset).distinct()

    def _orm_filter_search(self, queryset, value):
        return queryset.filter(
            Q(course_name__icontains=value) | Q(course_code__icontains=value)
        ).distinct()
