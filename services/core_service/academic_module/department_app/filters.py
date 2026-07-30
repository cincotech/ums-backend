import django_filters
from django.db.models import Q

from services.core_service.academic_module.faculty_app.models import Faculty
from services.search.filterset import TypesenseSearchFilterSet

from .models import Department


class DepartmentFilter(TypesenseSearchFilterSet):
    search = django_filters.CharFilter(method="filter_search")
    faculty = django_filters.ModelChoiceFilter(
        field_name="faculty",
        to_field_name="id",
        queryset=Faculty.objects.all(),
        label="Faculté",
    )

    class Meta:
        model = Department
        fields = ["faculty"]

    def _orm_filter_search(self, queryset, value):
        return queryset.filter(
            Q(department_name__icontains=value)
            | Q(faculty__faculty_name__icontains=value)
            | Q(abreviation__icontains=value)
        ).distinct()

    def filter_queryset(self, queryset):
        return super().filter_queryset(queryset).distinct()
