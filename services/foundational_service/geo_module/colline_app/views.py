from django.db.models import Q
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import OrderingFilter, SearchFilter
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from core.response_handler import validate_serializer
from services.foundational_service.geo_module.serializers import CollineSerializer
from services.foundational_service.geo_module.zone_app.models import Zone

from .models import Colline


class CollineListCreateAPIView(APIView):
    """Lister toutes les collines ou en créer une nouvelle"""

    def get(self, request):
        # Filtrage optionnel par zone
        zone_id = request.GET.get("zone_id")
        if zone_id:
            collines = Colline.objects.filter(zone_id=zone_id)
        else:
            collines = Colline.objects.all()
        serializer = CollineSerializer(collines, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def post(self, request):
        serializer = CollineSerializer(data=request.data)
        error = validate_serializer(serializer)
        if error:
            return error
        if serializer.is_valid():
            # Vérification que la zone existe avant la sauvegarde
            zone_id = serializer.validated_data.get("zone").id
            try:
                Zone.objects.get(id=zone_id)
            except Zone.DoesNotExist:
                return Response(
                    {"error": "Zone does not exist."},
                    status=status.HTTP_400_BAD_REQUEST,
                )
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class CollineDetailAPIView(APIView):
    """Récupérer, mettre à jour ou supprimer une colline spécifique"""

    def get_object(self, pk):
        try:
            return Colline.objects.get(pk=pk)
        except Colline.DoesNotExist:
            return None

    def get(self, request, pk):
        colline = self.get_object(pk)

        if not colline:
            return Response(
                {"detail": "Colline not found"}, status=status.HTTP_404_NOT_FOUND
            )
        serializer = CollineSerializer(colline)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def put(self, request, pk):
        colline = self.get_object(pk)
        if not colline:
            return Response(
                {"detail": "Colline not found"}, status=status.HTTP_404_NOT_FOUND
            )
        serializer = CollineSerializer(colline, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk):
        colline = self.get_object(pk)
        if not colline:
            return Response(
                {"detail": "Colline not found"}, status=status.HTTP_404_NOT_FOUND
            )
        colline.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
