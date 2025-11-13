# Create your views here.

from core.views import BaseViewSet

from .models import Department
from .serializers import DepartmentSerializer


class DepartmentViewSet(BaseViewSet):
    queryset = Department.objects.all()
    serializer_class = DepartmentSerializer
