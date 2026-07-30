from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.filters import OrderingFilter

from core.response_handler import error_response, success_response
from core.views import BaseViewSet
from services.search.backends import TypesenseFilterBackend

from .filters import ParentFilter, ProfessionFilter
from .models import Parent, Profession
from .serializers import ParentSerializer, ProfessionSerializer


class ProfessionViewSet(BaseViewSet):
    queryset = Profession.objects.all()
    serializer_class = ProfessionSerializer
    filter_backends = [DjangoFilterBackend, TypesenseFilterBackend, OrderingFilter]
    filterset_class = ProfessionFilter
    search_fields = ["profession_name"]
    filter_fields = ["faculty_id", "university_id"]
    ordering_fields = ["profession_name"]
    ordering = ["profession_name"]


class ParentViewSet(BaseViewSet):
    queryset = Parent.objects.all()
    serializer_class = ParentSerializer
    filter_backends = [DjangoFilterBackend, TypesenseFilterBackend, OrderingFilter]
    filterset_class = ParentFilter
    search_fields = ["parent_name", "parent_phone", "parent_email"]
    filter_fields = ["faculty_id", "university_id", "student_id"]
    ordering_fields = ["parent_name"]
    ordering = ["parent_name"]

    @action(
        detail=False, methods=["get"], url_path=r"by-student/(?P<student_id>[^/.]+)"
    )
    def by_student(self, request, student_id=None):
        """Return parents associated with a given student id."""
        try:
            parents = self.get_queryset().filter(students_parents__id=student_id)
            serializer = self.get_serializer(parents, many=True)
            return success_response(
                data=serializer.data,
                message=f"Parents for student {student_id} retrieved",
            )
        except Exception as e:
            return error_response(
                message="Error retrieving parents for student",
                errors={"detail": str(e)},
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )
