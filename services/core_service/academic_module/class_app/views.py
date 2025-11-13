# Create your views here.
from core.views import BaseViewSet

from .models import Class
from .serializers import ClassSerializer


class ClassViewSet(BaseViewSet):
    queryset = Class.objects.all()
    serializer_class = ClassSerializer
