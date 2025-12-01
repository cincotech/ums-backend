from core.views import BaseViewSet

from .models import Module, Semester
from .serializers import ModuleSerializer, SemesterSerializer


class SemesterViewSet(BaseViewSet):
    queryset = Semester.objects.all()
    serializer_class = SemesterSerializer


class ModuleViewSet(BaseViewSet):
    queryset = Module.objects.all()
    serializer_class = ModuleSerializer
