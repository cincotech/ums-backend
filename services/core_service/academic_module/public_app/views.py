from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import viewsets
from rest_framework.filters import OrderingFilter, SearchFilter
from rest_framework.permissions import IsAuthenticated

from services.foundational_service.auth_module.authorization_app.models import Profile

from .models import Program
from .serializers import ProfileSerializer, ProgramSerializer


class ProgramViewSet(viewsets.ModelViewSet):
    queryset = Program.objects.filter(is_active=True)
    serializer_class = ProgramSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ["faculty", "is_active"]
    search_fields = ["presentation"]
    ordering_fields = ["duration"]
    ordering = ["duration"]


class AcademicTeamViewSet(viewsets.ModelViewSet):
    queryset = Profile.objects.select_related("user", "faculty", "university")
    serializer_class = ProfileSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ["user__role", "faculty", "university"]
    search_fields = ["user__first_name", "user__last_name", "user__email", "position"]
    ordering_fields = ["user__first_name", "start_date"]
    ordering = ["user__first_name"]
