from django.db.models import Q
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import OrderingFilter, SearchFilter

from core.views import BaseViewSet

from .filters import TeacherFilter
from .models import Attribution, Suggestion, Teacher
from .serializers import AttributionSerializer, SuggestionSerializer, TeacherSerializer


class TeacherViewSet(BaseViewSet):
    queryset = Teacher.objects.all()
    serializer_class = TeacherSerializer
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    search_fields = [
        "user__first_name",
        "user__last_name",
        "user__email",
        "teacher_grade",
        "speciality",
    ]
    filterset_class = TeacherFilter
    ordering_fields = ["user__first_name", "user__last_name", "teacher_grade"]
    ordering = ["user__last_name"]

    def get_queryset(self):
        queryset = super().get_queryset()
        search = self.request.query_params.get("search")

        if search:
            queryset = queryset.filter(
                Q(user__first_name__icontains=search)
                | Q(user__last_name__icontains=search)
                | Q(user__email__icontains=search)
            )

        return queryset


class AttributionViewSet(BaseViewSet):
    queryset = Attribution.objects.all()
    serializer_class = AttributionSerializer


class SuggestionViewSet(BaseViewSet):
    queryset = Suggestion.objects.all()
    serializer_class = SuggestionSerializer
