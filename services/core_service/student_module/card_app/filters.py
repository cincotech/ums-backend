import django_filters
from django.db.models import Q
from .models import StudentCard


class StudentCardFilter(django_filters.FilterSet):
    search = django_filters.CharFilter(method='filter_search')
    
    class Meta:
        model = StudentCard
        fields = []
    
    def filter_search(self, queryset, name, value):
        return queryset.filter(
            Q(student__matricule__icontains=value) |
            Q(card_number__icontains=value) |
            Q(status__icontains=value)
        )
