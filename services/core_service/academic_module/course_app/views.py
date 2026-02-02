from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import OrderingFilter, SearchFilter

from core.views import BaseViewSet

from .filters import CourseFilter
from .models import Course
from .serializers import CourseSerializer


class CourseViewSet(BaseViewSet):
    queryset = Course.objects.all()
    serializer_class = CourseSerializer
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_class = CourseFilter
    search_fields = ["course_name", "course_code", "module__module_name"]
    ordering_fields = ["course_name", "course_code"]
    ordering = ["course_name"]
