import django_filters
from django.db.models import Q

from services.core_service.academic_module.department_app.models import Department
from services.core_service.academic_module.faculty_app.models import Faculty
from services.search.filterset import TypesenseSearchFilterSet

from .models import Class


class ClassFilter(TypesenseSearchFilterSet):
    search = django_filters.CharFilter(method="filter_search")
    type_formation = django_filters.CharFilter(
        field_name="department__faculty__types__code",
        lookup_expr="in",
    )
    department = django_filters.ModelChoiceFilter(
        field_name="department",
        to_field_name="id",
        queryset=Department.objects.all(),
        label="Département",
    )
    faculty = django_filters.ModelChoiceFilter(
        field_name="department__faculty",
        to_field_name="id",
        queryset=Faculty.objects.all(),
        label="Faculté",
    )

    class Meta:
        model = Class
        fields = ["type_formation", "department", "faculty"]

    def _orm_filter_search(self, queryset, value):
        return queryset.filter(
            Q(class_name__icontains=value)
            | Q(department__department_name__icontains=value)
        ).distinct()

    def filter_queryset(self, queryset):
        return super().filter_queryset(queryset).distinct()
