from datetime import date

import django_filters
from django.db.models import Q

from .models import Student


class StudentFilter(django_filters.FilterSet):
    # Search filter using Q objects
    search = django_filters.CharFilter(method="filter_search")

    # Filters based on inscription and related models
    academic_year_id = django_filters.UUIDFilter(
        field_name="inscriptions__academic_year_id", lookup_expr="exact"
    )
    faculty = django_filters.UUIDFilter(
        field_name="inscriptions__class_fk__department__faculty_id", lookup_expr="exact"
    )
    department = django_filters.UUIDFilter(
        field_name="inscriptions__class_fk__department_id", lookup_expr="exact"
    )
    className = django_filters.UUIDFilter(
        field_name="inscriptions__class_fk_id", lookup_expr="exact"
    )
    sexe = django_filters.CharFilter(field_name="user__gender", lookup_expr="exact")
    ageRange = django_filters.CharFilter(method="filter_age_range")

    # Additional filters aligned with InscriptionFilter
    regist_status = django_filters.CharFilter(
        field_name="inscriptions__regist_status", lookup_expr="exact"
    )
    class_name = django_filters.CharFilter(
        field_name="inscriptions__class_fk__class_name", lookup_expr="icontains"
    )
    date_inscription = django_filters.DateFilter(
        field_name="inscriptions__date_inscription", lookup_expr="exact"
    )
    date_inscription__gte = django_filters.DateFilter(
        field_name="inscriptions__date_inscription", lookup_expr="gte"
    )
    date_inscription__lte = django_filters.DateFilter(
        field_name="inscriptions__date_inscription", lookup_expr="lte"
    )
    is_year_close = django_filters.BooleanFilter(
        field_name="inscriptions__is_year_close"
    )

    class Meta:
        model = Student
        fields = []

    def filter_search(self, queryset, name, value):
        return queryset.filter(
            Q(user__first_name__icontains=value)
            | Q(user__last_name__icontains=value)
            | Q(user__email__icontains=value)
            | Q(matricules__matricule__icontains=value)
        )

    def filter_age_range(self, queryset, name, value):
        """
        Filter students by age range based on their birth date.
        Age ranges: less_than_nineteen, nineteen_to_twenty_two,
        twenty_three_to_twenty_six, twenty_seven_to_thirty, greater_than_thirty
        """
        age_range = value
        today = date.today()

        # Get distinct student IDs and birth dates to avoid duplicates from multiple inscriptions
        student_data = queryset.distinct().values_list("id", "user__birth_date")

        valid_ids = []
        for student_id, birth_date in student_data:
            if not birth_date:
                continue
            # Calculate age
            age = today.year - birth_date.year
            # Adjust if birthday hasn't occurred yet this year
            if (today.month, today.day) < (birth_date.month, birth_date.day):
                age -= 1

            if age_range == "less_than_nineteen" and age < 19:
                valid_ids.append(student_id)
            elif age_range == "nineteen_to_twenty_two" and 19 <= age <= 22:
                valid_ids.append(student_id)
            elif age_range == "twenty_three_to_twenty_six" and 23 <= age <= 26:
                valid_ids.append(student_id)
            elif age_range == "twenty_seven_to_thirty" and 27 <= age <= 30:
                valid_ids.append(student_id)
            elif age_range == "greater_than_thirty" and age > 30:
                valid_ids.append(student_id)

        return queryset.filter(id__in=valid_ids)

    @property
    def qs(self):
        """Ensure distinct results to avoid duplicates from joins"""
        return super().qs.distinct()
