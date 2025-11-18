from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from services.foundational_service.geo_module.commune_app.models import Commune
from services.foundational_service.geo_module.serializers import ZoneSerializer

from .models import Zone


class ZoneListCreateAPIView(APIView):
    """Lister toutes les zones ou en créer une nouvelle"""

    def get(self, request):
        # Filtrage optionnel par commune
        commune_id = request.GET.get("commune_id")
        if commune_id:
            zones = Zone.objects.filter(commune_id=commune_id)
        else:
            zones = Zone.objects.all()
        serializer = ZoneSerializer(zones, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def post(self, request):
        serializer = ZoneSerializer(data=request.data)
        if serializer.is_valid():
            # Vérification que la commune existe avant la sauvegarde
            commune_id = serializer.validated_data.get("commune").id
            try:
                Commune.objects.get(id=commune_id)
            except Commune.DoesNotExist:
                return Response(
                    {"error": "Commune does not exist."},
                    status=status.HTTP_400_BAD_REQUEST,
                )
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ZoneDetailAPIView(APIView):
    """Récupérer, mettre à jour ou supprimer une zone spécifique"""

    def get_object(self, pk):
        try:
            return Zone.objects.get(pk=pk)
        except Zone.DoesNotExist:
            return None

    def get(self, request, pk):
        zone = self.get_object(pk)
        if not zone:
            return Response(
                {"detail": "Zone not found"}, status=status.HTTP_404_NOT_FOUND
            )
        serializer = ZoneSerializer(zone)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def put(self, request, pk):
        zone = self.get_object(pk)
        if not zone:
            return Response(
                {"detail": "Zone not found"}, status=status.HTTP_404_NOT_FOUND
            )
        serializer = ZoneSerializer(zone, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk):
        zone = self.get_object(pk)
        if not zone:
            return Response(
                {"detail": "Zone not found"}, status=status.HTTP_404_NOT_FOUND
            )
        zone.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
