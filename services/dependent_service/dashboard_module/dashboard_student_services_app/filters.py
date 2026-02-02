import django_filters
from django.db.models import Q

from .models import (
    AbsenceJustification,
    CounselingSession,
    DocumentRequest,
    Scholarship,
    StudentActivity,
    StudentStatusChange,
)


class DocumentRequestFilter(django_filters.FilterSet):
    search = django_filters.CharFilter(method="filter_search")

    class Meta:
        model = DocumentRequest
        fields = []

    def filter_search(self, queryset, name, value):
        return queryset.filter(
            Q(student__matricule__icontains=value)
            | Q(document_type__icontains=value)
            | Q(status__icontains=value)
        )


class AbsenceJustificationFilter(django_filters.FilterSet):
    search = django_filters.CharFilter(method="filter_search")

    class Meta:
        model = AbsenceJustification
        fields = []

    def filter_search(self, queryset, name, value):
        return queryset.filter(
            Q(student__matricule__icontains=value)
            | Q(absence_type__icontains=value)
            | Q(status__icontains=value)
        )


class StudentActivityFilter(django_filters.FilterSet):
    search = django_filters.CharFilter(method="filter_search")

    class Meta:
        model = StudentActivity
        fields = []

    def filter_search(self, queryset, name, value):
        return queryset.filter(
            Q(name__icontains=value)
            | Q(activity_type__icontains=value)
            | Q(location__icontains=value)
        )


class ScholarshipFilter(django_filters.FilterSet):
    search = django_filters.CharFilter(method="filter_search")

    class Meta:
        model = Scholarship
        fields = []

    def filter_search(self, queryset, name, value):
        return queryset.filter(
            Q(student__matricule__icontains=value)
            | Q(scholarship_type__icontains=value)
            | Q(provider__icontains=value)
        )


class CounselingSessionFilter(django_filters.FilterSet):
    search = django_filters.CharFilter(method="filter_search")

    class Meta:
        model = CounselingSession
        fields = []

    def filter_search(self, queryset, name, value):
        return queryset.filter(
            Q(title__icontains=value)
            | Q(session_type__icontains=value)
            | Q(location__icontains=value)
        )


class StudentStatusChangeFilter(django_filters.FilterSet):
    search = django_filters.CharFilter(method="filter_search")

    class Meta:
        model = StudentStatusChange
        fields = []

    def filter_search(self, queryset, name, value):
        return queryset.filter(
            Q(student__matricule__icontains=value)
            | Q(status_type__icontains=value)
            | Q(approval_status__icontains=value)
        )


class PopulationDataFilter(django_filters.FilterSet):
    search = django_filters.CharFilter(method="filter_search")

    class Meta:
        model = None
        fields = []

    def filter_search(self, queryset, name, value):
        return queryset
