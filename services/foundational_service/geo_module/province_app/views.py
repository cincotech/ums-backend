from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from services.foundational_service.geo_module.country_app.models import Country
from services.foundational_service.geo_module.serializers import ProvinceSerializer

from .models import Province


class ProvinceListCreateAPIView(APIView):
    """Lister toutes les provinces ou en créer une nouvelle"""

    def get(self, request):
        country_id = request.GET.get("country_id")
        if country_id:
            provinces = Province.objects.filter(country_id=country_id)
        else:
            provinces = Province.objects.all()
        serializer = ProvinceSerializer(provinces, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def post(self, request):
        serializer = ProvinceSerializer(data=request.data)
        if serializer.is_valid():
            # Vérification que le pays existe avant la sauvegarde
            country_id = serializer.validated_data.get("country").id
            try:
                Country.objects.get(id=country_id)
            except Country.DoesNotExist:
                return Response(
                    {"error": "Country does not exist."},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ProvinceDetailAPIView(APIView):
    """Récupérer, mettre à jour ou supprimer une province spécifique"""

    def get_object(self, pk):
        try:
            return Province.objects.get(pk=pk)
        except Province.DoesNotExist:
            return None

    def get(self, request, pk):
        province = self.get_object(pk)
        if not province:
            return Response(
                {"detail": "Province not found"}, status=status.HTTP_404_NOT_FOUND
            )
        serializer = ProvinceSerializer(province)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def put(self, request, pk):
        province = self.get_object(pk)
        if not province:
            return Response(
                {"detail": "Province not found"}, status=status.HTTP_404_NOT_FOUND
            )
        serializer = ProvinceSerializer(province, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk):
        province = self.get_object(pk)
        if not province:
            return Response(
                {"detail": "Province not found"}, status=status.HTTP_404_NOT_FOUND
            )
        province.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
