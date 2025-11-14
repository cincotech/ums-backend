from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from .models import Room
from .serializers import RoomSerializer


class RoomViewSet(viewsets.ModelViewSet):
    """
    ViewSet pour gérer les salles (Rooms).
    Permet : list, retrieve, create, update, partial_update, destroy
    """
    queryset = Room.objects.select_related('building').all()
    serializer_class = RoomSerializer
    permission_classes = [IsAuthenticated]
