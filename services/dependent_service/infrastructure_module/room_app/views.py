from django.db.models import Q
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import OrderingFilter, SearchFilter
from rest_framework.permissions import IsAuthenticated

from core.permissions import IsGeneralService, IsSuperAdminOrGeneralService
from core.views import BaseViewSet

from .models import Room
from .serializers import RoomSerializer


class RoomViewSet(BaseViewSet):
    queryset = Room.objects.all()
    serializer_class = RoomSerializer

    def get_permissions(self):
        if self.request.method in ["GET", "HEAD", "OPTIONS"]:
            return [IsAuthenticated(), IsSuperAdminOrGeneralService()]
        return [IsAuthenticated(), IsGeneralService()]
