import django_filters
from django.db.models import Q
from .models import Student


class StudentFilter(django_filters.FilterSet):
    # Search filter using Q objects
    search = django_filters.CharFilter(method='filter_search')
    
    class Meta:
        model = Student
        fields = []
    
    def filter_search(self, queryset, name, value):
        return queryset.filter(
            Q(user__first_name__icontains=value) |
            Q(user__last_name__icontains=value) |
            Q(user__email__icontains=value) |
            Q(matricule__icontains=value)
        )
