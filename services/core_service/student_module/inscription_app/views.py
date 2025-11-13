# Create your views here.

from core.views import BaseViewSet

from .models import Inscription
from .serializers import InscriptionSerializer


class InscriptionViewSet(BaseViewSet):
    queryset = Inscription.objects.all()
    serializer_class = InscriptionSerializer
