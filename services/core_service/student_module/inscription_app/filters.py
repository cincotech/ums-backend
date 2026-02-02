import django_filters
from django.db.models import Q
from .models import Inscription


class InscriptionFilter(django_filters.FilterSet):
    # Exact filters
    student = django_filters.UUIDFilter(field_name='student')
    academic_year = django_filters.UUIDFilter(field_name='academic_year')
    class_fk = django_filters.UUIDFilter(field_name='class_fk')
    is_year_close = django_filters.BooleanFilter(field_name='is_year_close')
    date_inscription = django_filters.DateFilter(field_name='date_inscription')
    date_inscription__gte = django_filters.DateFilter(field_name='date_inscription', lookup_expr='gte')
    date_inscription__lte = django_filters.DateFilter(field_name='date_inscription', lookup_expr='lte')
    
    # Search filters (icontains)
    regist_status = django_filters.CharFilter(field_name='regist_status', lookup_expr='icontains')
    student_first_name = django_filters.CharFilter(field_name='student__user__first_name', lookup_expr='icontains')
    student_last_name = django_filters.CharFilter(field_name='student__user__last_name', lookup_expr='icontains')
    student_matricule = django_filters.CharFilter(field_name='student__matricule', lookup_expr='icontains')
    class_name = django_filters.CharFilter(field_name='class_fk__class_name', lookup_expr='icontains')
    
    # Q search - searches across multiple fields
    search = django_filters.CharFilter(method='filter_search')
    
    class Meta:
        model = Inscription
        fields = ['student', 'academic_year', 'class_fk', 'is_year_close', 'date_inscription']
    
    def filter_search(self, queryset, name, value):
        return queryset.filter(
            Q(student__user__first_name__icontains=value) |
            Q(student__user__last_name__icontains=value) |
            Q(student__matricule__icontains=value) |
            Q(class_fk__class_name__icontains=value) |
            Q(regist_status__icontains=value)
        )
