# Create your views here.
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import OrderingFilter, SearchFilter

from core.views import BaseViewSet

from .filters import ClassFilter
from .models import Class
from .serializers import ClassSerializer


class ClassViewSet(BaseViewSet):
    queryset = Class.objects.all()
    serializer_class = ClassSerializer
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_class = ClassFilter
    search_fields = [
        "class_name",
        "department__department_name",
        "department__faculty__faculty_name",
    ]
    ordering_fields = ["class_name"]
    ordering = ["class_name"]
