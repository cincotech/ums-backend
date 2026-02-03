import django_filters
from django.db.models import Q

from .models import Course


class CourseFilter(django_filters.FilterSet):
    # Search filter using Q objects
    search = django_filters.CharFilter(method="filter_search")

    class Meta:
        model = Course
        fields = []

    def filter_search(self, queryset, name, value):
        return queryset.filter(
            Q(course_name__icontains=value)
            | Q(course_code__icontains=value)
            | Q(teacher__user__last_name__icontains=value)
        )
