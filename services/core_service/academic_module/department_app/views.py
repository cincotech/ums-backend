# Create your views here.

from django_filters.rest_framework import DjangoFilterBackend

from core.views import BaseViewSet

from .models import Department
from .serializers import DepartmentSerializer


class DepartmentViewSet(BaseViewSet):
    queryset = Department.objects.all()
    serializer_class = DepartmentSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ["faculty_id"]

    def get_queryset(self):
        qs = Department.objects.all()
        faculty_id = self.request.query_params.get("faculty_id")

        if faculty_id:
            qs = qs.filter(faculty_id=faculty_id)

        return qs
