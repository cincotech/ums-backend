import django_filters
from django.db.models import Q

from services.core_service.academic_module.course_app.models import Course


class CourseFilter(django_filters.FilterSet):
    search = django_filters.CharFilter(method="filter_search")

    class Meta:
        model = Course
        fields = []

    def filter_search(self, queryset, name, value):
        return queryset.filter(
            Q(course_name__icontains=value) | Q(course_code__icontains=value)
        )
