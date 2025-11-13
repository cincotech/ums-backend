# Create your views here.
from core.views import BaseViewSet

from .models import Module
from .serializers import ModuleSerializer


class ModuleViewSet(BaseViewSet):
    queryset = Module.objects.all()
    serializer_class = ModuleSerializer
