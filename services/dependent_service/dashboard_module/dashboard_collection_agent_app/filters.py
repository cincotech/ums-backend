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
    status = django_filters.CharFilter(field_name="status", lookup_expr="iexact")

    class Meta:
        model = Bank
        fields = ["status"]

    def filter_search(self, queryset, name, value):
        return queryset.filter(
            Q(bank_name__icontains=value)
            | Q(bank_abreviation__icontains=value)
            | Q(account_number__icontains=value)
        )


class WordingFilter(django_filters.FilterSet):
    search = django_filters.CharFilter(method="filter_search")
    wording_name = django_filters.CharFilter(
        field_name="wording_name", lookup_expr="icontains"
    )

    class Meta:
        model = Wording
        fields = ["wording_name"]

    def filter_search(self, queryset, name, value):
        return queryset.filter(Q(wording_name__icontains=value))


class FeesSheetFilter(django_filters.FilterSet):
    search = django_filters.CharFilter(method="filter_search")
    class_fk = django_filters.UUIDFilter(field_name="class_fk")
    department = django_filters.UUIDFilter(field_name="department")
    faculty = django_filters.UUIDFilter(field_name="faculty")
    academic_year = django_filters.UUIDFilter(field_name="academic_year")
    wording = django_filters.UUIDFilter(field_name="wording")

    class Meta:
        model = FeesSheet
        fields = ["class_fk", "department", "faculty", "academic_year", "wording"]

    def filter_search(self, queryset, name, value):
        return queryset.filter(
            Q(wording__wording_name__icontains=value) | Q(base_amount__icontains=value)
        )


class PaymentInstallementFilter(django_filters.FilterSet):
    search = django_filters.CharFilter(method="filter_search")
    payment_plan = django_filters.UUIDFilter(field_name="payment_plan")
    student = django_filters.UUIDFilter(field_name="student")
    status = django_filters.CharFilter(field_name="status", lookup_expr="iexact")
    class_id = django_filters.UUIDFilter(method="filter_by_class")
    department_id = django_filters.UUIDFilter(method="filter_by_department")
    faculty_id = django_filters.UUIDFilter(method="filter_by_faculty")
    academic_year_id = django_filters.UUIDFilter(method="filter_by_academic_year")

    class Meta:
        model = PaymentInstallement
        fields = ["payment_plan", "student", "status", "academic_year_id"]

    def filter_search(self, queryset, name, value):
        return queryset.filter(
            Q(student__matricule__icontains=value) | Q(status__icontains=value)
        )

    def filter_by_class(self, queryset, name, value):
        return queryset.filter(
            student__inscriptions__class_fk=value,
            student__inscriptions__regist_status__in=["Active", "Pending"],
        ).distinct()

    def filter_by_department(self, queryset, name, value):
        return queryset.filter(
            student__inscriptions__class_fk__department=value,
            student__inscriptions__regist_status__in=["Active", "Pending"],
        ).distinct()

    def filter_by_faculty(self, queryset, name, value):
        return queryset.filter(
            student__inscriptions__class_fk__department__faculty=value,
            student__inscriptions__regist_status__in=["Active", "Pending"],
        ).distinct()

    def filter_by_academic_year(self, queryset, name, value):
        return queryset.filter(
            student__inscriptions__academic_year=value,
            student__inscriptions__regist_status__in=["Active", "Pending"],
        ).distinct()


class PaymentReminderFilter(django_filters.FilterSet):
    search = django_filters.CharFilter(method="filter_search")
    student = django_filters.UUIDFilter(field_name="student")
    reminder_type = django_filters.CharFilter(
        field_name="reminder_type", lookup_expr="iexact"
    )
    status = django_filters.CharFilter(field_name="status", lookup_expr="iexact")

    class Meta:
        model = PaymentReminder
        fields = ["student", "reminder_type", "status"]

    def filter_search(self, queryset, name, value):
        return queryset.filter(
            Q(student__matricule__icontains=value) | Q(reminder_type__icontains=value)
        )


class PaymentPlanFilter(django_filters.FilterSet):
    search = django_filters.CharFilter(method="filter_search")
    feessheet = django_filters.UUIDFilter(field_name="feessheet")
    status = django_filters.CharFilter(field_name="status", lookup_expr="iexact")
    created_by = django_filters.UUIDFilter(field_name="created_by")
    class_id = django_filters.UUIDFilter(method="filter_by_class")
    department_id = django_filters.UUIDFilter(method="filter_by_department")
    faculty_id = django_filters.UUIDFilter(method="filter_by_faculty")
    academic_year_id = django_filters.UUIDFilter(field_name="feessheet__academic_year")

    class Meta:
        model = PaymentPlan
        fields = ["feessheet", "status", "created_by", "academic_year_id"]

    def filter_search(self, queryset, name, value):
        return queryset.filter(
            Q(description__icontains=value) | Q(status__icontains=value)
        )

    def filter_by_class(self, queryset, name, value):
        return queryset.filter(feessheet__class_fk=value)

    def filter_by_department(self, queryset, name, value):
        return queryset.filter(feessheet__department=value)

    def filter_by_faculty(self, queryset, name, value):
        return queryset.filter(feessheet__faculty=value)


class PaymentPromiseFilter(django_filters.FilterSet):
    search = django_filters.CharFilter(method="filter_search")
    student = django_filters.UUIDFilter(field_name="student")
    status = django_filters.CharFilter(field_name="status", lookup_expr="iexact")
    promised_date = django_filters.DateFilter(field_name="promised_date")

    class Meta:
        model = PaymentPromise
        fields = ["student", "status", "promised_date"]

    def filter_search(self, queryset, name, value):
        return queryset.filter(
            Q(student__matricule__icontains=value) | Q(status__icontains=value)
        )


class PaymentFilter(django_filters.FilterSet):
    search = django_filters.CharFilter(method="filter_search")
    payment_status = django_filters.CharFilter(
        field_name="payment_status", lookup_expr="iexact"
    )
    payment_method = django_filters.CharFilter(
        field_name="payment_method", lookup_expr="iexact"
    )
    paymentplan = django_filters.UUIDFilter(field_name="paymentplan")
    inscription = django_filters.UUIDFilter(field_name="inscription")
    bank = django_filters.UUIDFilter(field_name="bank")
    user = django_filters.UUIDFilter(field_name="user")
    academic_year_id = django_filters.UUIDFilter(field_name="inscription__academic_year")

    class Meta:
        model = Payment
        fields = [
            "payment_status",
            "payment_method",
            "paymentplan",
            "inscription",
            "bank",
            "user",
            "academic_year_id",
        ]

    def filter_search(self, queryset, name, value):
        return queryset.filter(
            Q(inscription__student__matricule__icontains=value)
            | Q(payment_method__icontains=value)
            | Q(payment_status__icontains=value)
            | Q(transaction_code__icontains=value)
        )


class CollectionCorrespondenceFilter(django_filters.FilterSet):
    search = django_filters.CharFilter(method="filter_search")
    student = django_filters.UUIDFilter(field_name="student")
    correspondence_type = django_filters.CharFilter(
        field_name="correspondence_type", lookup_expr="iexact"
    )

    class Meta:
        model = CollectionCorrespondence
        fields = ["student", "correspondence_type"]

    def filter_search(self, queryset, name, value):
        return queryset.filter(
            Q(student__matricule__icontains=value)
            | Q(subject__icontains=value)
            | Q(correspondence_type__icontains=value)
        )
