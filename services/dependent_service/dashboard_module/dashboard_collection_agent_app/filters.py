import django_filters
from django.db.models import Q

from .models import (
    Bank,
    CollectionCorrespondence,
    FeesSheet,
    Payment,
    PaymentInstallement,
    PaymentPlan,
    PaymentPromise,
    PaymentReminder,
    Wording,
)


class BankFilter(django_filters.FilterSet):
    search = django_filters.CharFilter(method="filter_search")

    class Meta:
        model = Bank
        fields = []

    def filter_search(self, queryset, name, value):
        return queryset.filter(
            Q(bank_name__icontains=value)
            | Q(bank_abreviation__icontains=value)
            | Q(account_number__icontains=value)
        )


class WordingFilter(django_filters.FilterSet):
    search = django_filters.CharFilter(method="filter_search")

    class Meta:
        model = Wording
        fields = []

    def filter_search(self, queryset, name, value):
        return queryset.filter(Q(wording_name__icontains=value))


class FeesSheetFilter(django_filters.FilterSet):
    search = django_filters.CharFilter(method="filter_search")

    class Meta:
        model = FeesSheet
        fields = []

    def filter_search(self, queryset, name, value):
        return queryset.filter(
            Q(wording__wording_name__icontains=value) | Q(base_amount__icontains=value)
        )


class PaymentInstallementFilter(django_filters.FilterSet):
    search = django_filters.CharFilter(method="filter_search")

    class Meta:
        model = PaymentInstallement
        fields = []

    def filter_search(self, queryset, name, value):
        return queryset.filter(
            Q(student__matricule__icontains=value) | Q(status__icontains=value)
        )


class PaymentReminderFilter(django_filters.FilterSet):
    search = django_filters.CharFilter(method="filter_search")

    class Meta:
        model = PaymentReminder
        fields = []

    def filter_search(self, queryset, name, value):
        return queryset.filter(
            Q(student__matricule__icontains=value) | Q(reminder_type__icontains=value)
        )


class PaymentPlanFilter(django_filters.FilterSet):
    search = django_filters.CharFilter(method="filter_search")

    class Meta:
        model = PaymentPlan
        fields = []

    def filter_search(self, queryset, name, value):
        return queryset.filter(
            Q(description__icontains=value) | Q(status__icontains=value)
        )


class PaymentPromiseFilter(django_filters.FilterSet):
    search = django_filters.CharFilter(method="filter_search")

    class Meta:
        model = PaymentPromise
        fields = []

    def filter_search(self, queryset, name, value):
        return queryset.filter(
            Q(student__matricule__icontains=value) | Q(status__icontains=value)
        )


class PaymentFilter(django_filters.FilterSet):
    search = django_filters.CharFilter(method="filter_search")

    class Meta:
        model = Payment
        fields = []

    def filter_search(self, queryset, name, value):
        return queryset.filter(
            Q(inscription__student__matricule__icontains=value)
            | Q(payment_method__icontains=value)
            | Q(payment_status__icontains=value)
            | Q(transaction_code__icontains=value)
        )


class CollectionCorrespondenceFilter(django_filters.FilterSet):
    search = django_filters.CharFilter(method="filter_search")

    class Meta:
        model = CollectionCorrespondence
        fields = []

    def filter_search(self, queryset, name, value):
        return queryset.filter(
            Q(student__matricule__icontains=value)
            | Q(subject__icontains=value)
            | Q(correspondence_type__icontains=value)
        )
