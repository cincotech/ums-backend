import django_filters
from django.db.models import Q
from django.contrib.auth import get_user_model

User = get_user_model()


class UserFilter(django_filters.FilterSet):
    # Search filter using Q objects
    search = django_filters.CharFilter(method='filter_search')
    
    class Meta:
        model = User
        fields = []
    
    def filter_search(self, queryset, name, value):
        return queryset.filter(
            Q(email__icontains=value) |
            Q(first_name__icontains=value) |
            Q(last_name__icontains=value) |
            Q(phone_number__icontains=value)
        )
