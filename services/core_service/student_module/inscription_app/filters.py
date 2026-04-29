import django_filters
from django.db.models import Q
from datetime import date

from .models import Inscription


class InscriptionFilter(django_filters.FilterSet):
    # Exact filters
    student = django_filters.UUIDFilter(field_name="student")
    academic_year = django_filters.UUIDFilter(field_name="academic_year")
    class_fk = django_filters.UUIDFilter(field_name="class_fk")
    is_year_close = django_filters.BooleanFilter(field_name="is_year_close")
    date_inscription = django_filters.DateFilter(field_name="date_inscription")
    date_inscription__gte = django_filters.DateFilter(
        field_name="date_inscription", lookup_expr="gte"
    )
    date_inscription__lte = django_filters.DateFilter(
        field_name="date_inscription", lookup_expr="lte"
    )

    # Additional filters for consistency with StudentFilter
    faculty = django_filters.UUIDFilter(
        field_name="class_fk__department__faculty_id", lookup_expr="exact"
    )
    department = django_filters.UUIDFilter(
        field_name="class_fk__department_id", lookup_expr="exact"
    )
    className = django_filters.UUIDFilter(
        field_name="class_fk_id", lookup_expr="exact"
    )
    sexe = django_filters.CharFilter(
        field_name="student__user__gender", lookup_expr="exact"
    )
    ageRange = django_filters.CharFilter(method="filter_age_range")

    # Search filters (icontains)
    regist_status = django_filters.CharFilter(
        field_name="regist_status", lookup_expr="icontains"
    )
    student_first_name = django_filters.CharFilter(
        field_name="student__user__first_name", lookup_expr="icontains"
    )
    student_last_name = django_filters.CharFilter(
        field_name="student__user__last_name", lookup_expr="icontains"
    )
    student_matricule = django_filters.CharFilter(
        field_name="student__matricule", lookup_expr="icontains"
    )
    class_name = django_filters.CharFilter(
        field_name="class_fk__class_name", lookup_expr="icontains"
    )

    # Q search - searches across multiple fields
    search = django_filters.CharFilter(method="filter_search")

    class Meta:
        model = Inscription
        fields = [
            "student",
            "academic_year",
            "class_fk",
            "is_year_close",
            "date_inscription",
            "faculty",
            "department",
            "className",
            "sexe",
            "ageRange",
            "regist_status",
        ]

    def filter_search(self, queryset, name, value):
        return queryset.filter(
            Q(student__user__first_name__icontains=value)
            | Q(student__user__last_name__icontains=value)
            | Q(student__matricule__icontains=value)
            | Q(class_fk__class_name__icontains=value)
            | Q(regist_status__icontains=value)
        )

    def filter_age_range(self, queryset, name, value):
        """
        Filter inscriptions by student age range based on birth date.
        Age ranges: less_than_nineteen, nineteen_to_twenty_two,
        twenty_three_to_twenty_six, twenty_seven_to_thirty, greater_than_thirty
        """
        age_range = value
        today = date.today()
        
        # Build age filters using annotations would be more efficient,
        # but we'll use a subquery approach for correctness
        from django.db.models import Subquery, OuterRef
        
        # Get all distinct student IDs in the queryset
        student_ids = queryset.values_list('student_id', flat=True).distinct()
        
        # Filter students by age range
        valid_student_ids = []
        for student in Inscription.objects.filter(student_id__in=student_ids).select_related('student__user'):
            birth_date = student.student.user.birth_date
            if not birth_date:
                continue
            age = today.year - birth_date.year
            if (today.month, today.day) < (birth_date.month, birth_date.day):
                age -= 1
            
            if age_range == "less_than_nineteen" and age < 19:
                valid_student_ids.append(student.student_id)
            elif age_range == "nineteen_to_twenty_two" and 19 <= age <= 22:
                valid_student_ids.append(student.student_id)
            elif age_range == "twenty_three_to_twenty_six" and 23 <= age <= 26:
                valid_student_ids.append(student.student_id)
            elif age_range == "twenty_seven_to_thirty" and 27 <= age <= 30:
                valid_student_ids.append(student.student_id)
            elif age_range == "greater_than_thirty" and age > 30:
                valid_student_ids.append(student.student_id)
        
        return queryset.filter(student_id__in=valid_student_ids)
