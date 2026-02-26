import django_filters
from django.db.models import Q

from .models import Parent, Profession


class ParentFilter(django_filters.FilterSet):
    search = django_filters.CharFilter(method="filter_search")
    student_id = django_filters.UUIDFilter(
        field_name="students_parents__id", lookup_expr="exact"
    )

    class Meta:
        model = Parent
        fields = []

    def filter_search(self, queryset, name, value):
        return queryset.filter(
            Q(parent_name__icontains=value)
            | Q(parent_phone__icontains=value)
            | Q(parent_email__icontains=value)
        )


class ProfessionFilter(django_filters.FilterSet):
    search = django_filters.CharFilter(method="filter_search")

    class Meta:
        model = Profession
        fields = []

    def filter_search(self, queryset, name, value):
        return queryset.filter(Q(profession_name__icontains=value))
