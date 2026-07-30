import django_filters
from django.db.models import Q

from services.core_service.academic_module.department_app.models import Department
from services.core_service.academic_module.faculty_app.models import Faculty
from services.search.filterset import TypesenseSearchFilterSet

from .models import Class, Module, Semester


class ModuleFilter(TypesenseSearchFilterSet):
    # Full-text search via Typesense or ORM fallback
    search = django_filters.CharFilter(method="filter_search")

    # Filtres relationnels directs
    class_fk = django_filters.ModelChoiceFilter(
        field_name="class_fk",
        to_field_name="id",
        queryset=Class.objects.all(),
        label="Classe",
    )
    semester = django_filters.ModelChoiceFilter(
        field_name="semester",
        to_field_name="id",
        queryset=Semester.objects.all(),
        label="Semestre",
    )

    # Filtres relationnels à travers les relations
    department = django_filters.ModelChoiceFilter(
        field_name="class_fk__department",
        to_field_name="id",
        queryset=Department.objects.all(),
        label="Département",
    )
    faculty = django_filters.ModelChoiceFilter(
        field_name="class_fk__department__faculty",
        to_field_name="id",
        queryset=Faculty.objects.all(),
        label="Faculté",
    )

    class Meta:
        model = Module
        fields = ["class_fk", "semester", "department", "faculty"]

    def filter_queryset(self, queryset):
        return super().filter_queryset(queryset).distinct()

    def _orm_filter_search(self, queryset, value):
        return queryset.filter(
            Q(module_name__icontains=value) | Q(code__icontains=value)
        ).distinct()
