from django.core.exceptions import ValidationError
from django.utils import timezone
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.decorators import action
from rest_framework.filters import OrderingFilter, SearchFilter
from rest_framework.response import Response
from rest_framework import status

from core.response_handler import error_response, success_response, validate_serializer
from core.views import BaseViewSet
from services.core_service.academic_module.university_app.models import AcademicYear

from .email_utils import send_inscription_email
from .filters import InscriptionFilter
from .models import Class, Inscription
from .serializers import InscriptionSerializer
from .inscription_template_service import generate_inscription_template
from .annual_registration_service import AnnualRegistrationService


class InscriptionViewSet(BaseViewSet):
    queryset = Inscription.objects.all()
    serializer_class = InscriptionSerializer
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_class = InscriptionFilter
    search_fields = [
        "student__user__first_name",
        "student__user__last_name",
        "student__matricules__matricule",
        "class_fk__class_name",
    ]
    ordering_fields = ["date_inscription", "regist_status"]
    ordering = ["-date_inscription"]

    def get_closed_year_warning(self, academic_year):
        if academic_year and academic_year.is_closed:
            return (
                "Attention : cette inscription est enregistrée dans une année "
                "académique déjà fermée. Elle restera visible dans les archives "
                "de cette année."
            )
        return None

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        validation_error = validate_serializer(serializer)
        if validation_error:
            return validation_error

        self.perform_create(serializer)
        inscription = serializer.instance
        message = (
            self.get_closed_year_warning(inscription.academic_year)
            or "Inscription créée avec succès"
        )
        return success_response(
            data=serializer.data,
            message=message,
            status_code=status.HTTP_201_CREATED,
        )

    def get_queryset(self):
        queryset = super().get_queryset()

        if getattr(self, "action", None) != "list":
            return queryset

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

        allowed_statuses = ["Pending", "Suspended"]

        if inscription.regist_status not in allowed_statuses:
            return error_response(
                message=(
                    f"This inscription cannot be activated because "
                    f"its current status is '{inscription.regist_status}'. "
                    f"Only Pending or Suspended inscriptions can be activated."
                )
            )

        try:
            # Determine whether payment verification should be skipped
            skip_payment = (
                request.user
                and hasattr(request.user, "role")
                and request.user.role
                and request.user.role.name == "student_service"
            )

            with transaction.atomic():

                # Activate inscription
                inscription.activate(
                    skip_payment_check=skip_payment
                )

                # Generate matricule if missing
                matricule = inscription.generate_matricule()

                # Send email only after successful transaction
                transaction.on_commit(
                    lambda: send_inscription_email(
                        inscription,
                        "Active"
                    )
                )

            return success_response(
                message=(
                    "The inscription has been successfully activated. "
                    "The student can now access academic services."
                ),
                data={
                    "inscription": InscriptionSerializer(inscription).data,
                    "matricule": matricule,
                    "status": inscription.regist_status,
                },
            )

        except ValidationError as e:

            return error_response(
                message=(
                    "The inscription could not be activated because "
                    "one or more business rules failed."
                ),
                errors=e.message_dict if hasattr(e, "message_dict") else str(e),
            )

        except Exception as e:

            return error_response(
                message=(
                    "An unexpected error occurred while activating "
                    "the inscription."
                ),
                errors=str(e),
            )

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

        messages = {
            "Completed": "Impossible de remplacer : l'inscription est déjà terminée.",
            "Withdrawn": "Impossible de remplacer : l'étudiant s'est retiré.",
            "Dropped": "Impossible de remplacer : l'étudiant a abandonné.",
            "Suspended": "Impossible de remplacer : l'inscription est suspendue.",
            "Canceled": "Impossible de remplacer : l'inscription est annulée.",
            "Replaced": "Impossible de remplacer : l'inscription a déjà été remplacée.",
            "Complement": "Impossible de remplacer : l'inscription est en complément.",
        }
        return error_response(
            message=messages.get(
                inscription.regist_status,
                f"Impossible de remplacer : statut '{inscription.regist_status}' non autorisé.",
            )
        )

    @action(detail=True, methods=["post"])
    def transfer_academic_year(self, request, pk=None):
        inscription = self.get_object()
        academic_year_id = request.data.get("academic_year_id")
        if not academic_year_id:
            return error_response(message="academic_year_id is required")

        try:
            target_academic_year = AcademicYear.objects.get(id=academic_year_id)
        except AcademicYear.DoesNotExist:
            return error_response(message="Année académique introuvable")

        try:
            transferred = inscription.transfer_academic_year(
                target_academic_year,
                user=request.user,
            )
            message = (
                self.get_closed_year_warning(target_academic_year)
                or "Inscription transférée vers l'année académique sélectionnée"
            )
            return success_response(
                message=message,
                data=InscriptionSerializer(transferred).data,
            )
        except ValidationError as e:
            return error_response(message=" ".join(e.messages))

    @action(detail=True, methods=["post"])
    def annual_registration(self, request, pk=None):
        source_inscription = self.get_object()
        academic_year_id = request.data.get("academic_year_id")
        class_id = request.data.get("class_fk_id") or request.data.get("class_id")
        mode = request.data.get("mode")
        date_inscription = request.data.get("date_inscription")

        if not academic_year_id:
            return error_response(message="academic_year_id is required")
        if not class_id:
            return error_response(message="class_fk_id is required")
        if not mode:
            return error_response(message="mode is required")

        try:
            target_academic_year = AcademicYear.objects.get(id=academic_year_id)
        except AcademicYear.DoesNotExist:
            return error_response(message="Année académique introuvable")

        try:
            target_class = Class.objects.get(id=class_id)
        except Class.DoesNotExist:
            return error_response(message="Classe introuvable")

        try:
            result = AnnualRegistrationService.create_next_registration(
                source_inscription=source_inscription,
                target_academic_year=target_academic_year,
                target_class=target_class,
                mode=mode,
                date_inscription=date_inscription,
                created_by=request.user,
            )
            return success_response(
                message=result["message"],
                data={
                    "inscription": InscriptionSerializer(result["inscription"]).data,
                    "created": result["created"],
                    "decision": result["decision"],
                    "payment_required": result["payment_required"],
                },
            )
        except ValidationError as e:
            return error_response(message=" ".join(e.messages))

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
        
       
