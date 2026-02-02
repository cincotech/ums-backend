# Create your views here.

from django.db.models import Q
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import OrderingFilter, SearchFilter

from core.views import BaseViewSet

from .models import Department
from .serializers import DepartmentSerializer
from .filters import DepartmentFilter


class DepartmentViewSet(BaseViewSet):
    queryset = Department.objects.all()
    serializer_class = DepartmentSerializer
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_class = DepartmentFilter
    search_fields = ['department_name', 'abreviation', 'faculty__faculty_name']
    ordering_fields = ['department_name']
    ordering = ['department_name']

    def get_queryset(self):
        qs = Department.objects.all()
        faculty_id = self.request.query_params.get("faculty_id")

        if faculty_id:
            qs = qs.filter(faculty_id=faculty_id)

        return qs
