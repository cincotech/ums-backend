# Create your views here.

from core.views import BaseViewSet

from .models import Faculty, TypeFormation
from .serializers import FacultySerializer, TypeFormationSerializer


class TypeFormationViewSet(BaseViewSet):
    queryset = TypeFormation.objects.all()
    serializer_class = TypeFormationSerializer


class FacultyViewSet(BaseViewSet):
    queryset = Faculty.objects.all()
    serializer_class = FacultySerializer
