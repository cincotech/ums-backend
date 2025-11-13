from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .models import Country
from services.foundational_service.geo_module.serializers import CountrySerializer
from core.response_handler import validate_serializer, success_response
from core.exception_handler import custom_exception_handler
class CountryListCreateAPIView(APIView):
    """Lister tous les pays ou en créer un nouveau"""

    def get(self, request):
       try:
        countries = Country.objects.all()
        serializer = CountrySerializer(countries, many=True)
        return success_response(
            data=serializer.data,
            message="list of countries retrieved successfully",
            status_code=status.HTTP_200_OK
        )
       except Exception as exc:
              
            response = custom_exception_handler(exc, {"view": self})
            if response is not None:
                return response
            raise 
    def post(self, request):
      try:
        serializer = CountrySerializer(data=request.data)
        error=validate_serializer(serializer)
        if error:
            return error
    
        serializer.save()
        return success_response(
                data=serializer.data, 
                message="country created successfully",
                status_code=status.HTTP_201_CREATED)
      except Exception as exc:
            response = custom_exception_handler(exc, {"view": self})
            if response is not None:
                return response
            raise 


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
        return success_response(
            data=serializer.data, 
            message="countries retrieved successfully",
            status_code=status.HTTP_200_OK
        )

    def put(self, request, pk):
        country = self.get_object(pk)
        if not country:
            return Response({"detail": "Country not found"}, status=status.HTTP_404_NOT_FOUND)
        serializer = CountrySerializer(country, data=request.data)
        error=validate_serializer()
        if error:
            return error
        if serializer.is_valid():
            serializer.save()
            return success_response(
                data=serializer.data, 
                message="country updated successfully",
                status_code=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk):
        country = self.get_object(pk)
        if not country:
            return Response({"detail": "Country not found"}, status=status.HTTP_404_NOT_FOUND)
        country.delete()
        return success_response(
            message="country deleted successfully",
            status_code=status.HTTP_204_NO_CONTENT
        )
