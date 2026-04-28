import django_filters
from django.db.models import Q

from .models import Module


class ModuleFilter(django_filters.FilterSet):
    # Search filter using Q objects
    search = django_filters.CharFilter(method="filter_search")

    class Meta:
        model = Module
        fields = []

    def filter_search(self, queryset, name, value):
        return queryset.filter(
            Q(module_name__icontains=value) | Q(code__icontains=value)
        )
