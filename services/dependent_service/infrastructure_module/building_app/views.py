from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from .models import Building
from .serializers import BuildingSerializer


class BuildingAPIView(APIView):
    """
    API pour gérer les bâtiments (utilisateur connecté requis) :
    - GET: lister tous les bâtiments ou un bâtiment spécifique (si id dans JSON)
    - POST: créer un bâtiment
    - PUT: mettre à jour un bâtiment (id dans JSON)
    - DELETE: supprimer un bâtiment (id dans JSON)
    """

    permission_classes = [IsAuthenticated]

    def get(self, request):
        building_id = request.data.get('id')
        if building_id:
            try:
                building = Building.objects.select_related('university').get(pk=building_id)
            except Building.DoesNotExist:
                return Response({"detail": "Not found"}, status=status.HTTP_404_NOT_FOUND)
            serializer = BuildingSerializer(building)
            return Response(serializer.data)
        else:
            buildings = Building.objects.select_related('university').all()
            serializer = BuildingSerializer(buildings, many=True)
            return Response(serializer.data)

    def post(self, request):
        serializer = BuildingSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def put(self, request):
        building_id = request.data.get('id')
        if not building_id:
            return Response({"detail": "Missing building id"}, status=status.HTTP_400_BAD_REQUEST)

        try:
            building = Building.objects.get(pk=building_id)
        except Building.DoesNotExist:
            return Response({"detail": "Not found"}, status=status.HTTP_404_NOT_FOUND)

        serializer = BuildingSerializer(building, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request):
        building_id = request.data.get('id')
        if not building_id:
            return Response({"detail": "Missing building id"}, status=status.HTTP_400_BAD_REQUEST)

        try:
            building = Building.objects.get(pk=building_id)
        except Building.DoesNotExist:
            return Response({"detail": "Not found"}, status=status.HTTP_404_NOT_FOUND)

        building.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
