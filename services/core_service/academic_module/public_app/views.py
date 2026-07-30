from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import viewsets
from rest_framework.filters import OrderingFilter
from rest_framework.permissions import IsAuthenticated

from services.foundational_service.auth_module.authorization_app.models import Profile
from services.search.backends import TypesenseFilterBackend

from .models import Program
from .serializers import ProfileSerializer, ProgramSerializer


class ProgramViewSet(viewsets.ModelViewSet):
    queryset = Program.objects.filter(is_active=True)
    serializer_class = ProgramSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, TypesenseFilterBackend, OrderingFilter]
    filterset_fields = ["faculty", "is_active"]
    search_fields = ["presentation"]
    filter_fields = ["faculty_id", "university_id"]
    ordering_fields = ["duration"]
    ordering = ["duration"]


class AcademicTeamViewSet(viewsets.ModelViewSet):
    queryset = Profile.objects.select_related("user", "faculty", "university")
    serializer_class = ProfileSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, TypesenseFilterBackend, OrderingFilter]
    filterset_fields = ["user__role", "faculty", "university"]
    search_fields = ["user__first_name", "user__last_name", "user__email", "position"]
    filter_fields = ["faculty_id", "university_id"]
    ordering_fields = ["user__first_name", "start_date"]
    ordering = ["user__first_name"]
