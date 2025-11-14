from rest_framework import viewsets, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.exceptions import NotFound
from .models import Room
from .serializers import RoomSerializer
from core.response_handler import (
    success_response,
    error_response,
    validate_serializer,
)


class RoomViewSet(viewsets.ModelViewSet):
    """
    ViewSet pour gérer les salles (Rooms).
    Permet : list, retrieve, create, update, partial_update, destroy
    """
    queryset = Room.objects.select_related('building').all()
    serializer_class = RoomSerializer
    permission_classes = [IsAuthenticated]

    def list(self, request):
        queryset = self.get_queryset()
        serializer = self.serializer_class(queryset, many=True)
        return success_response(
            data=serializer.data,
            message="Liste des salles récupérée avec succès."
        )

    def retrieve(self, request, pk=None):
        try:
            room = self.get_object()
        except NotFound:
            return error_response(
                message="Salle introuvable.",
                status_code=status.HTTP_404_NOT_FOUND,
            )
        serializer = self.serializer_class(room)
        return success_response(
            data=serializer.data,
            message="Salle récupérée avec succès."
        )

    def create(self, request):
        serializer = self.serializer_class(data=request.data)
        validation_error = validate_serializer(serializer)
        if validation_error:
            return validation_error
        serializer.save()
        return success_response(
            data=serializer.data,
            message="Salle créée avec succès.",
            status_code=status.HTTP_201_CREATED,
        )

    def update(self, request, pk=None):
        try:
            room = self.get_object()
        except NotFound:
            return error_response(
                message="Salle introuvable.",
                status_code=status.HTTP_404_NOT_FOUND,
            )
        serializer = self.serializer_class(room, data=request.data)
        validation_error = validate_serializer(serializer)
        if validation_error:
            return validation_error
        serializer.save()
        return success_response(
            data=serializer.data,
            message="Salle mise à jour avec succès.",
        )

    def partial_update(self, request, pk=None):
        try:
            room = self.get_object()
        except NotFound:
            return error_response(
                message="Salle introuvable.",
                status_code=status.HTTP_404_NOT_FOUND,
            )
        serializer = self.serializer_class(room, data=request.data, partial=True)
        validation_error = validate_serializer(serializer)
        if validation_error:
            return validation_error
        serializer.save()
        return success_response(
            data=serializer.data,
            message="Salle partiellement mise à jour avec succès.",
        )

    def destroy(self, request, pk=None):
        try:
            room = self.get_object()
        except NotFound:
            return error_response(
                message="Salle introuvable.",
                status_code=status.HTTP_404_NOT_FOUND,
            )
        room.delete()
        return success_response(
            message="Salle supprimée avec succès.",
            status_code=status.HTTP_204_NO_CONTENT,
        )
