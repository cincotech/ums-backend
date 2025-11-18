from rest_framework.permissions import IsAuthenticated

from core.permissions import IsGeneralService, IsSuperAdmin
from core.views import BaseViewSet

from .models import Room
from .serializers import RoomSerializer


class RoomViewSet(BaseViewSet):
    queryset = Room.objects.all()
    serializer_class = RoomSerializer

    def get_permissions(self):
        if self.request.method in ["GET", "HEAD", "OPTIONS"]:
            return [IsAuthenticated(), IsSuperAdmin() | IsGeneralService()]
        return [IsAuthenticated(), IsGeneralService()]
