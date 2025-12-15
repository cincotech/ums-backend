from django.utils import timezone
from rest_framework.decorators import action

from core.response_handler import error_response, success_response  # your helpers
from core.views import BaseViewSet
from services.core_service.academic_module.university_app.models import AcademicYear

from .models import Class, Inscription
from .serializers import InscriptionSerializer


class InscriptionViewSet(BaseViewSet):
    queryset = Inscription.objects.all()
    serializer_class = InscriptionSerializer

    def list(self, request, *args, **kwargs):
        academic_year_id = request.query_params.get("academic_year_id")

        queryset = self.queryset

        if academic_year_id:
            queryset = queryset.filter(academic_year_id=academic_year_id)
        else:
            try:
                current_year = AcademicYear.objects.get(
                    start_date__lte=timezone.now(),
                    end_date__gte=timezone.now(),
                )
                queryset = queryset.filter(academic_year=current_year)
            except AcademicYear.DoesNotExist:
                queryset = queryset.none()

        serializer = self.get_serializer(queryset.distinct(), many=True)
        return success_response(
            data=serializer.data,
            message="Inscription list retrieved successfully",
        )

    # ---------------------------
    # Custom actions using model methods
    # ---------------------------
    @action(detail=True, methods=["post"])
    def activate(self, request, pk=None):
        inscription = self.get_object()
        if inscription.regist_status in ["Pending", "Suspended"]:
            inscription.activate()
            inscription.generate_matricule()
            return success_response(
                message="Inscription activated",
                data=InscriptionSerializer(inscription).data,
            )
        return error_response(message="Cannot activate")

    @action(detail=True, methods=["post"])
    def complete(self, request, pk=None):
        inscription = self.get_object()
        if inscription.is_active():
            inscription.complete()
            return success_response(
                message="Inscription completed",
                data=InscriptionSerializer(inscription).data,
            )
        return error_response(message="Cannot complete")

    @action(detail=True, methods=["post"])
    def withdraw(self, request, pk=None):
        inscription = self.get_object()
        if inscription.regist_status in ["Active", "Pending"]:
            inscription.withdraw()
            return success_response(
                message="Inscription withdrawn",
                data=InscriptionSerializer(inscription).data,
            )
        return error_response(message="Cannot withdraw")

    @action(detail=True, methods=["post"])
    def drop(self, request, pk=None):
        inscription = self.get_object()
        if inscription.is_active():
            inscription.drop()
            return success_response(
                message="Inscription dropped",
                data=InscriptionSerializer(inscription).data,
            )
        return error_response(message="Cannot drop")

    @action(detail=True, methods=["post"])
    def suspend(self, request, pk=None):
        inscription = self.get_object()
        if inscription.is_active():
            inscription.suspend()
            return success_response(
                message="Inscription suspended",
                data=InscriptionSerializer(inscription).data,
            )
        return error_response(message="Cannot suspend")

    @action(detail=True, methods=["post"])
    def cancel(self, request, pk=None):
        inscription = self.get_object()
        if inscription.regist_status in ["Pending", "Active"]:
            inscription.cancel()
            return success_response(
                message="Inscription canceled",
                data=InscriptionSerializer(inscription).data,
            )
        return error_response(message="Cannot cancel")

    @action(detail=True, methods=["post"])
    def replace(self, request, pk=None):
        inscription = self.get_object()
        new_class_id = request.data.get("new_class_id")
        if not new_class_id:
            return error_response(message="new_class_id is required")

        try:
            new_class = Class.objects.get(id=new_class_id)
        except Class.DoesNotExist:
            return error_response(message="Invalid class ID")

        if inscription.regist_status in ["Active", "Pending"]:
            new_inscription = inscription.replace(new_class)
            new_inscription.generate_matricule()
            return success_response(
                message="Inscription replaced",
                data={"new_inscription_id": str(new_inscription.id)},
            )

        return error_response(message="Cannot replace")
