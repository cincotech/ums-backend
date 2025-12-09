# Create your views here.

from core.views import BaseViewSet

from .models import Student, StudentGraduateInfo, StudentHsInfo, Training
from .serializers import (
    StudentGraduateInfoSerializer,
    StudentHsInfoSerializer,
    StudentSerializer,
    TrainingSerializer,
)


class StudentViewSet(BaseViewSet):
    queryset = Student.objects.all()
    serializer_class = StudentSerializer

    def perform_create(self, serializer):

        return serializer.save()


class TrainingViewSet(BaseViewSet):
    queryset = Training.objects.all()
    serializer_class = TrainingSerializer


class StudentHsInfoViewSet(BaseViewSet):
    queryset = StudentHsInfo.objects.all()
    serializer_class = StudentHsInfoSerializer


class StudentGraduateInfoViewSet(BaseViewSet):
    queryset = StudentGraduateInfo.objects.all()
    serializer_class = StudentGraduateInfoSerializer
