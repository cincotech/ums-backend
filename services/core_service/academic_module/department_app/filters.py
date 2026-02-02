import django_filters
from django.db.models import Q
from .models import Department


class DepartmentFilter(django_filters.FilterSet):
    # Search filter using Q objects
    search = django_filters.CharFilter(method='filter_search')
    
    class Meta:
        model = Department
        fields = []
    
    def filter_search(self, queryset, name, value):
        return queryset.filter(
            Q(department_name__icontains=value) |
            Q(department_code__icontains=value) |
            Q(faculty__faculty_name__icontains=value)
        )
