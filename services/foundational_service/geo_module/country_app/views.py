from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .models import Country
from services.foundational_service.geo_module.serializers import CountrySerializer


class CountryListCreateAPIView(APIView):
    """Lister tous les pays ou en créer un nouveau"""

    def get(self, request):
        countries = Country.objects.all()
        serializer = CountrySerializer(countries, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def post(self, request):
        serializer = CountrySerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class CountryDetailAPIView(APIView):
    """Récupérer, mettre à jour ou supprimer un pays spécifique"""

    def get_object(self, pk):
        try:
            return Country.objects.get(pk=pk)
        except Country.DoesNotExist:
            return None

    def get(self, request, pk):
        country = self.get_object(pk)
        if not country:
            return Response({"detail": "Country not found"}, status=status.HTTP_404_NOT_FOUND)
        serializer = CountrySerializer(country)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def put(self, request, pk):
        country = self.get_object(pk)
        if not country:
            return Response({"detail": "Country not found"}, status=status.HTTP_404_NOT_FOUND)
        serializer = CountrySerializer(country, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk):
        country = self.get_object(pk)
        if not country:
            return Response({"detail": "Country not found"}, status=status.HTTP_404_NOT_FOUND)
        country.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
