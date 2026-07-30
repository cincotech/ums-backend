import django_filters
from django.db.models import Q

from services.search.filterset import TypesenseSearchFilterSet

from .models import Teacher


class TeacherFilter(TypesenseSearchFilterSet):
    # Search filter using Q objects
    search = django_filters.CharFilter(method="filter_search")

    class Meta:
        model = Teacher
        fields = []

    def _orm_filter_search(self, queryset, value):
        return queryset.filter(
            Q(user__first_name__icontains=value)
            | Q(user__last_name__icontains=value)
            | Q(user__email__icontains=value)
            | Q(speciality__icontains=value)
        )
