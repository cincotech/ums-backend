from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView

from core.permissions import IsGeneralService, IsSuperAdmin
from core.response_handler import error_response, success_response, validate_serializer

from .models import Building
from .serializers import BuildingSerializer


class BuildingAPIView(APIView):
    """
    API pour gérer les bâtiments :
    - GET: liste ou détail (accessible à general_service et super_admin)
    - POST/PUT/DELETE: accessible uniquement à super_admin
    """

    permission_classes = [IsAuthenticated]

    def get_permissions(self):
        """
        Retourne les permissions dynamiquement selon la méthode HTTP.
        """
        if self.request.method == "GET":
            return [IsAuthenticated(), IsSuperAdmin() | IsGeneralService()]
        return [IsAuthenticated(), IsSuperAdmin()]

    def get(self, request):
        building_id = request.data.get("id")
        if building_id:
            try:
                building = Building.objects.select_related("university").get(
                    pk=building_id
                )
                serializer = BuildingSerializer(building)
                return success_response(
                    data=serializer.data, message="Bâtiment récupéré avec succès."
                )
            except Building.DoesNotExist:
                return error_response(message="Bâtiment introuvable.", status_code=404)
        else:
            buildings = Building.objects.select_related("university").all()
            serializer = BuildingSerializer(buildings, many=True)
            return success_response(
                data=serializer.data,
                message="Liste des bâtiments récupérée avec succès.",
            )

    def post(self, request):
        serializer = BuildingSerializer(data=request.data)
        validation_error = validate_serializer(serializer)
        if validation_error:
            return validation_error

        serializer.save()
        return success_response(
            data=serializer.data, message="Bâtiment créé avec succès.", status_code=201
        )

    def put(self, request):
        building_id = request.data.get("id")
        if not building_id:
            return error_response(
                message="L'identifiant du bâtiment est requis.", status_code=400
            )

        try:
            building = Building.objects.get(pk=building_id)
        except Building.DoesNotExist:
            return error_response(message="Bâtiment introuvable.", status_code=404)

        serializer = BuildingSerializer(building, data=request.data)
        validation_error = validate_serializer(serializer)
        if validation_error:
            return validation_error

        serializer.save()
        return success_response(
            data=serializer.data, message="Bâtiment mis à jour avec succès."
        )

    def delete(self, request):
        building_id = request.data.get("id")
        if not building_id:
            return error_response(
                message="L'identifiant du bâtiment est requis.", status_code=400
            )

        try:
            building = Building.objects.get(pk=building_id)
        except Building.DoesNotExist:
            return error_response(message="Bâtiment introuvable.", status_code=404)

        building.delete()
        return success_response(
            message="Bâtiment supprimé avec succès.", status_code=204
        )
