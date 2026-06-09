import django_filters
from django.db.models import Q

from services.core_service.student_module.inscription_app.models import Inscription
from services.dependent_service.exam_module.exam_app.models import Exam

from .models import GradeComplaint, JurySession, OfficialDocument, TeacherPaymentClaim


class JurySessionFilter(django_filters.FilterSet):
    search = django_filters.CharFilter(method="filter_search")
    academic_year_id = django_filters.UUIDFilter(
        field_name="class_group__academic_year_id"
    )

    class Meta:
        model = JurySession
        fields = ["academic_year_id"]

    def filter_search(self, queryset, name, value):
        return queryset.filter(
            Q(session_name__icontains=value)
            | Q(class_group__class_fk__class_name__icontains=value)
            | Q(status__icontains=value)
        )


class GradeComplaintFilter(django_filters.FilterSet):
    search = django_filters.CharFilter(method="filter_search")
    # filter complaints by the student's inscriptions academic year
    academic_year_id = django_filters.UUIDFilter(
        field_name="student__inscriptions__academic_year_id",
        lookup_expr="exact",
    )

    class Meta:
        model = GradeComplaint
        fields = ["academic_year_id"]

    def filter_search(self, queryset, name, value):
        return queryset.filter(
            Q(student__matricule__icontains=value)
            | Q(course__course_name__icontains=value)
            | Q(status__icontains=value)
        )


class OfficialDocumentFilter(django_filters.FilterSet):
    search = django_filters.CharFilter(method="filter_search")
    # OfficialDocument has no student/academic_year relation; remove academic_year filter

    class Meta:
        model = OfficialDocument
        fields = []

    def filter_search(self, queryset, name, value):
        return queryset.filter(
            Q(title__icontains=value)
            | Q(document_type__icontains=value)
            | Q(status__icontains=value)
        )


class PaymentClaimFilter(django_filters.FilterSet):
    search = django_filters.CharFilter(method="filter_search")
    # Filter by teacher's attributions academic_year (Attribution.academic_year)
    academic_year_id = django_filters.UUIDFilter(
        field_name="teacher__principal_attributions__academic_year_id",
        lookup_expr="exact",
    )

    class Meta:
        model = TeacherPaymentClaim
        fields = ["academic_year_id"]

    def filter_search(self, queryset, name, value):
        return queryset.filter(
            Q(teacher__user__first_name__icontains=value)
            | Q(teacher__user__last_name__icontains=value)
            | Q(course__course_name__icontains=value)
            | Q(status__icontains=value)
        )


class InscriptionFilter(django_filters.FilterSet):
    search = django_filters.CharFilter(method="filter_search")
    # Inscription has its own academic_year FK
    academic_year_id = django_filters.UUIDFilter(
        field_name="academic_year_id",
        lookup_expr="exact",
    )

    class Meta:
        model = Inscription
        fields = ["academic_year_id"]

    def filter_search(self, queryset, name, value):
        return queryset.filter(
            Q(student__matricule__icontains=value)
            | Q(student__user__first_name__icontains=value)
            | Q(student__user__last_name__icontains=value)
            | Q(regist_status__icontains=value)
        )


class ExamFilter(django_filters.FilterSet):
    search = django_filters.CharFilter(method="filter_search")
    # Exam has an `academic_year` FK
    academic_year_id = django_filters.UUIDFilter(
        field_name="academic_year_id",
        lookup_expr="exact",
    )

    class Meta:
        model = Exam
        fields = ["academic_year_id"]

    def filter_search(self, queryset, name, value):
        return queryset
