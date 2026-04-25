from rest_framework.permissions import IsAuthenticated

from core.permissions import IsSuperAdminOrGeneralService
from core.views import BaseViewSet

from .models import Room
from .serializers import RoomSerializer


class RoomViewSet(BaseViewSet):
    queryset = Room.objects.all()
    serializer_class = RoomSerializer

    def get_permissions(self):
        return [IsAuthenticated(), IsSuperAdminOrGeneralService()]
