import django_filters
from django.db.models import Q

from services.core_service.student_module.inscription_app.models import Inscription

from .models import GradeComplaint, JurySession, OfficialDocument, TeacherPaymentClaim


class JurySessionFilter(django_filters.FilterSet):
    search = django_filters.CharFilter(method="filter_search")

    class Meta:
        model = JurySession
        fields = []

    def filter_search(self, queryset, name, value):
        return queryset.filter(
            Q(session_name__icontains=value)
            | Q(class_group__class_fk__class_name__icontains=value)
            | Q(status__icontains=value)
        )


class GradeComplaintFilter(django_filters.FilterSet):
    search = django_filters.CharFilter(method="filter_search")

    class Meta:
        model = GradeComplaint
        fields = []

    def filter_search(self, queryset, name, value):
        return queryset.filter(
            Q(student__matricule__icontains=value)
            | Q(course__course_name__icontains=value)
            | Q(status__icontains=value)
        )


class OfficialDocumentFilter(django_filters.FilterSet):
    search = django_filters.CharFilter(method="filter_search")

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

    class Meta:
        model = TeacherPaymentClaim
        fields = []

    def filter_search(self, queryset, name, value):
        return queryset.filter(
            Q(teacher__user__first_name__icontains=value)
            | Q(teacher__user__last_name__icontains=value)
            | Q(course__course_name__icontains=value)
            | Q(status__icontains=value)
        )


class InscriptionFilter(django_filters.FilterSet):
    search = django_filters.CharFilter(method="filter_search")

    class Meta:
        model = Inscription
        fields = []

    def filter_search(self, queryset, name, value):
        return queryset.filter(
            Q(student__matricule__icontains=value)
            | Q(student__user__first_name__icontains=value)
            | Q(student__user__last_name__icontains=value)
            | Q(regist_status__icontains=value)
        )


class ExamFilter(django_filters.FilterSet):
    search = django_filters.CharFilter(method="filter_search")

    class Meta:
        model = None
        fields = []

    def filter_search(self, queryset, name, value):
        return queryset
