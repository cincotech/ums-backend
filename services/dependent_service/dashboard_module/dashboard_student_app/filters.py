import django_filters
from django.db.models import Q
from .models import *


class PaymentFilter(django_filters.FilterSet):
    search = django_filters.CharFilter(method='filter_search')
    
    class Meta:
        model = Payment
        fields = []
    
    def filter_search(self, queryset, name, value):
        return queryset.filter(
            Q(student__matricule__icontains=value) |
            Q(payment_type__icontains=value) |
            Q(status__icontains=value)
        )


