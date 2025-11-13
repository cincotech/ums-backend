# Create your views here.

from core.views import BaseViewSet

from .models import Parent, Profession
from .serializers import ParentSerializer, ProfessionSerializer


class ProfessionViewSet(BaseViewSet):
    queryset = Profession.objects.all()
    serializer_class = ProfessionSerializer


class ParentViewSet(BaseViewSet):
    queryset = Parent.objects.all()
    serializer_class = ParentSerializer
