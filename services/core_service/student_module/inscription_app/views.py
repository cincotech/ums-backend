from django.utils import timezone
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.decorators import action
from rest_framework.filters import OrderingFilter, SearchFilter
from rest_framework.response import Response
from rest_framework import status

from core.response_handler import error_response, success_response
from core.views import BaseViewSet
from services.core_service.academic_module.university_app.models import AcademicYear

from .email_utils import send_inscription_email
from .filters import InscriptionFilter
from .models import Class, Inscription
from .serializers import InscriptionSerializer
from .inscription_template_service import generate_inscription_template


class InscriptionViewSet(BaseViewSet):
    queryset = Inscription.objects.all()
    serializer_class = InscriptionSerializer
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_class = InscriptionFilter
    search_fields = [
        "student__user__first_name",
        "student__user__last_name",
        "student__matricule",
        "class_fk__class_name",
    ]
    ordering_fields = ["date_inscription", "regist_status", "student__matricule"]
    ordering = ["-date_inscription"]

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
            try:
                # Skip payment check if user is student_service
                skip_payment = (request.user and 
                               hasattr(request.user, 'role') and 
                               request.user.role and 
                               request.user.role.name == "student_service")
                inscription.activate(skip_payment_check=skip_payment)
                inscription.generate_matricule()
                send_inscription_email(inscription, "Active")
                return success_response(
                    message="Inscription activated and email sent",
                    data=InscriptionSerializer(inscription).data,
                )
            except ValidationError as e:
                return error_response(message=str(e))
        return error_response(message="Cannot activate")

    @action(detail=True, methods=["post"])
    def complete(self, request, pk=None):
        inscription = self.get_object()
        if inscription.is_active():
            inscription.complete()
            send_inscription_email(inscription, "Completed")
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
            send_inscription_email(inscription, "Withdrawn")
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
            send_inscription_email(inscription, "Dropped")
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
            send_inscription_email(inscription, "Suspended")
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
            send_inscription_email(inscription, "Canceled")
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
            send_inscription_email(new_inscription, "Replaced")
            return success_response(
                message="Inscription replaced and email sent",
                data={"new_inscription_id": str(new_inscription.id)},
            )

        return error_response(message="Cannot replace")

    @action(detail=True, methods=["post"])
    def send_email(self, request, pk=None):
        """Envoyer manuellement l'email pour le statut actuel"""
        inscription = self.get_object()
        email_type = request.data.get("email_type", inscription.regist_status)

        if send_inscription_email(inscription, email_type):
            return success_response(message="Email envoyé avec succès")
        return error_response(message="Erreur lors de l'envoi de l'email")
    
    @action(detail=False, methods=["post"])
    def generate_inscription_template(self, request):
        inscription_id = request.data.get("inscription_id")
        academic_year_id = request.query_params.get("academic_year_id")

        if not inscription_id:
            return error_response(
                message="inscription_id is required",  
            )

        try:
            # On va chercher l'inscription et récupérer user_id
            inscription = Inscription.objects.filter(id=inscription_id).select_related("student__user").first()
            if not inscription:
                return error_response(
                    message="Inscription not found",
                )
            user_id = str(inscription.student.user.id)
            # Passer l'inscription_id au service
            data = generate_inscription_template(user_id, academic_year_id, inscription_id)
            return success_response(
                message="Template generated successfully",
                data=data
            )
        except Exception as e:
            return error_response(
                message=str(e),
            )
        
       