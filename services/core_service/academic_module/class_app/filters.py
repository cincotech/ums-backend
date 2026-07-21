import django_filters
from django.db.models import Q

from .models import Class


class ClassFilter(django_filters.FilterSet):
    # Search filter using Q objects
    search = django_filters.CharFilter(method="filter_search")
    type_formation = django_filters.CharFilter(
        field_name="department__faculty__types__code",
        lookup_expr="in",
    )

    class Meta:
        model = Class
        fields = ["type_formation"]

    def filter_search(self, queryset, name, value):
        return queryset.filter(
            Q(class_name__icontains=value)
            | Q(department__department_name__icontains=value)
        )
