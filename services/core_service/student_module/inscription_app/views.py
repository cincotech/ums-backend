from django.utils import timezone
from django.db.models import Q
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import OrderingFilter, SearchFilter
from rest_framework.decorators import action
from rest_framework import status

from core.response_handler import error_response, success_response, validate_serializer
from core.views import BaseViewSet
from services.core_service.academic_module.university_app.models import AcademicYear

from .models import Class, Inscription
from .serializers import InscriptionSerializer
from .filters import InscriptionFilter


class InscriptionViewSet(BaseViewSet):
    queryset = Inscription.objects.all()
    serializer_class = InscriptionSerializer
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_class = InscriptionFilter
    search_fields = ['student__user__first_name', 'student__user__last_name', 'student__matricule', 'class_fk__class_name']
    ordering_fields = ['date_inscription', 'regist_status', 'student__matricule']
    ordering = ['-date_inscription']

    def get_queryset(self):
        queryset = super().get_queryset()
        academic_year_id = self.request.query_params.get("academic_year_id")

        if academic_year_id:
            return queryset.filter(academic_year_id=academic_year_id)
        
        try:
            current_year = AcademicYear.objects.get(
                start_date__lte=timezone.now(),
                end_date__gte=timezone.now(),
            )
            return queryset.filter(academic_year=current_year)
        except AcademicYear.DoesNotExist:
            return queryset.none()

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
