# Create your views here.
from core.views import BaseViewSet

from .models import Course
from .serializers import CourseSerializer


class CourseViewSet(BaseViewSet):
    queryset = Course.objects.all()
    serializer_class = CourseSerializer
