import django_filters
from django.contrib.auth import get_user_model
from django.db.models import Q

from services.dependent_service.dashboard_module.dashboard_super_admin_app.models import (
    AuditLog,
)

from .models import UniversityConfiguration, UniversityNotification

User = get_user_model()


class ConfigurationFilter(django_filters.FilterSet):
    search = django_filters.CharFilter(method="filter_search")

    class Meta:
        model = UniversityConfiguration
        fields = []

    def filter_search(self, queryset, name, value):
        return queryset.filter(Q(key__icontains=value) | Q(category__icontains=value))


class StatisticsFilter(django_filters.FilterSet):
    search = django_filters.CharFilter(method="filter_search")

    class Meta:
        model = None
        fields = []

    def filter_search(self, queryset, name, value):
        return queryset


class NotificationFilter(django_filters.FilterSet):
    search = django_filters.CharFilter(method="filter_search")

    class Meta:
        model = UniversityNotification
        fields = []

    def filter_search(self, queryset, name, value):
        return queryset.filter(
            Q(title__icontains=value)
            | Q(message__icontains=value)
            | Q(notification_type__icontains=value)
        )


class AuditLogFilter(django_filters.FilterSet):
    search = django_filters.CharFilter(method="filter_search")

    class Meta:
        model = AuditLog
        fields = []

    def filter_search(self, queryset, name, value):
        return queryset.filter(
            Q(user__email__icontains=value)
            | Q(action__icontains=value)
            | Q(model_name__icontains=value)
        )


class BackupFilter(django_filters.FilterSet):
    search = django_filters.CharFilter(method="filter_search")

    class Meta:
        model = None
        fields = []

    def filter_search(self, queryset, name, value):
        return queryset


class UserFilter(django_filters.FilterSet):
    search = django_filters.CharFilter(method="filter_search")

    class Meta:
        model = User
        fields = []

    def filter_search(self, queryset, name, value):
        return queryset.filter(
            Q(email__icontains=value)
            | Q(first_name__icontains=value)
            | Q(last_name__icontains=value)
            | Q(phone_number__icontains=value)
        )


class StudentUserFilter(django_filters.FilterSet):
    search = django_filters.CharFilter(method="filter_search")

    class Meta:
        model = User
        fields = []

    def filter_search(self, queryset, name, value):
        return queryset.filter(
            Q(email__icontains=value)
            | Q(first_name__icontains=value)
            | Q(last_name__icontains=value)
            | Q(student__matricule__icontains=value)
        )


class RoleFilter(django_filters.FilterSet):
    search = django_filters.CharFilter(method="filter_search")

    class Meta:
        model = None
        fields = []

    def filter_search(self, queryset, name, value):
        return queryset


class RoleProfileFilter(django_filters.FilterSet):
    search = django_filters.CharFilter(method="filter_search")

    class Meta:
        model = None
        fields = []

    def filter_search(self, queryset, name, value):
        return queryset
