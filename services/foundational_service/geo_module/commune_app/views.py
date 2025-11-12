from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from services.foundational_service.geo_module.commune_app.models import Commune
from services.foundational_service.geo_module.serializers import CommuneSerializer


class CommuneListCreateAPIView(APIView):
    """Lister toutes les communes ou en créer une nouvelle"""

    def get(self, request):
        communes = Commune.objects.all()
        serializer = CommuneSerializer(communes, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def post(self, request):
        serializer = CommuneSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class CommuneDetailAPIView(APIView):
    """Récupérer, mettre à jour ou supprimer une commune spécifique"""

    def get_object(self, pk):
        try:
            return Commune.objects.get(pk=pk)
        except Commune.DoesNotExist:
            return None

    def get(self, request, pk):
        commune = self.get_object(pk)
        if not commune:
            return Response({"detail": "Commune not found"}, status=status.HTTP_404_NOT_FOUND)
        serializer = CommuneSerializer(commune)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def put(self, request, pk):
        commune = self.get_object(pk)
        if not commune:
            return Response({"detail": "Commune not found"}, status=status.HTTP_404_NOT_FOUND)
        serializer = CommuneSerializer(commune, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk):
        commune = self.get_object(pk)
        if not commune:
            return Response({"detail": "Commune not found"}, status=status.HTTP_404_NOT_FOUND)
        commune.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

