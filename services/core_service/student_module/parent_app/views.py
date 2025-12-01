# Create your views here.

from rest_framework.filters import SearchFilter
from rest_framework.permissions import IsAuthenticated

from core.views import BaseViewSet

from .models import Parent, Profession
from .serializers import ParentSerializer, ProfessionSerializer


class ProfessionViewSet(BaseViewSet):
    queryset = Profession.objects.all()
    serializer_class = ProfessionSerializer
    permission_classes = [IsAuthenticated]


class ParentViewSet(BaseViewSet):
    queryset = Parent.objects.all()
    serializer_class = ParentSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [SearchFilter]
    search_fields = ["parent_name", "parent_phone", "parent_email"]
