from django.core.exceptions import ValidationError
from django.db import transaction
from django.utils import timezone
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from services.core_service.student_module.inscription_app.models import Inscription as InscriptionType
    from services.core_service.academic_module.university_app.models import AcademicYear as AcademicYearType
from services.core_service.academic_module.class_app.models import Class
from services.core_service.academic_module.university_app.models import AcademicYear
from services.core_service.student_module.inscription_app.models import Inscription


class AnnualRegistrationService:
    PROMOTED = "promoted"
    REPEAT = "repeat"
    MODES = {PROMOTED, REPEAT}

    @classmethod
    def create_next_registration(
        cls,
        *,
        source_inscription,
        target_academic_year,
        target_class,
        mode,
        created_by=None,
        date_inscription=None,
    ):
        if mode not in cls.MODES:
            raise ValidationError("Mode invalide. Utilisez promoted ou repeat.")

        with transaction.atomic():
            source = (
                Inscription.objects.select_for_update()
                .select_related(
                    "student",
                    "academic_year",
                    "class_fk__department__faculty__types",
                    "class_group",
                )
                .get(pk=source_inscription.pk)
            )
            target_class = (
                Class.objects.select_related("department__faculty__types")
                .select_for_update()
                .get(pk=target_class.pk)
            )
            target_academic_year = AcademicYear.objects.select_for_update().get(
                pk=target_academic_year.pk
            )

            cls._validate_year(source, target_academic_year)
            cls._validate_source_status(source)
            decision_context = cls._get_decision_context(source)
            cls._validate_decision(mode, decision_context)
            cls._validate_class_transition(source, target_class, mode)

            existing = (
                Inscription.objects.select_for_update()
                .filter(
                    student=source.student,
                    academic_year=target_academic_year,
                    class_fk=target_class,
                )
                .first()
            )
            if existing:
                payment_required = not existing.has_verified_payment()
                message = (
                    "Une inscription existe déjà pour cet étudiant, cette classe "
                    "et cette année académique. Aucune nouvelle ligne n'a été créée."
                )
                if target_academic_year.is_closed:
                    message += (
                        " Attention : l'année académique cible est fermée, "
                        "l'inscription reste dans les archives de cette année."
                    )
                if payment_required:
                    message += (
                        " Les frais d'inscription restent dus pour cette année académique."
                    )
                return {
                    "inscription": existing,
                    "created": False,
                    "message": message,
                    "decision": decision_context,
                    "payment_required": payment_required,
                }

            inscription = Inscription(
                student=source.student,
                academic_year=target_academic_year,
                class_fk=target_class,
                date_inscription=date_inscription or timezone.now().date(),
                regist_status="Pending",
                created_by=created_by,
                modified_by=created_by,
                modified_at=timezone.now() if created_by else None,
            )
            inscription.clean()
            inscription.class_group = inscription.get_or_create_default_group()
            super(Inscription, inscription).save()
            inscription.generate_matricule()

            cls._close_source_year(source, created_by)

            message = cls._build_success_message(
                mode=mode,
                target_academic_year=target_academic_year,
            )
            return {
                "inscription": inscription,
                "created": True,
                "message": message,
                "decision": decision_context,
                "payment_required": True,
            }

    @staticmethod
    def _validate_year(source:"InscriptionType", target_academic_year:"AcademicYear"):
        if source.academic_year_id == target_academic_year.id:
            raise ValidationError(
                "La réinscription annuelle doit cibler une autre année académique."
            )

    @staticmethod
    def _validate_source_status(source):
        if source.regist_status in ["Canceled", "Withdrawn", "Dropped", "Replaced"]:
            raise ValidationError(
                f"Impossible de créer une réinscription depuis une inscription {source.regist_status}."
            )

    @staticmethod
    def _get_decision_context(source: "InscriptionType"):
        from services.dependent_service.dashboard_module.dashboard_academic_secretary_app.models import (
            JuryDecision,
        )
        from services.dependent_service.exam_module.result_app.models import CompiledResult

        jury_decision = None
        if source.class_group_id:
            jury_decision = (
                JuryDecision.objects.filter(
                    student=source.student,
                    jury_session__class_group=source.class_group,
                )
                .order_by("-validated_at")
                .first()
            )

        compiled_result = (
            CompiledResult.objects.filter(inscription=source)
            .order_by("-id")
            .first()
        )

        return {
            "jury_decision": jury_decision.decision if jury_decision else None,
            "compiled_status": compiled_result.status if compiled_result else None,
            "is_promoted": bool(compiled_result.is_promoted) if compiled_result else False,
        }

    @staticmethod
    def _validate_decision(mode, decision_context):
        jury_decision = decision_context["jury_decision"]
        compiled_status = decision_context["compiled_status"]
        is_promoted = decision_context["is_promoted"]
        # Nouveau: bloquer uniquement les décisions explicites 'AAA' (assimile aux ajournés)
        # et 'ND' (non décision). Tous les autres codes sont considérés autorisés
        # pour démarrer le processus de réinscription, sous réserve des vérifications
        # complémentaires ci-dessous.
        if jury_decision in ("AAA", "ND"):
            raise ValidationError(
                "Réinscription refusée : décision du jury non autorisée (AAA ou ND)."
            )

        if mode == AnnualRegistrationService.PROMOTED:
            # Pour la promotion, accepter si la décision du jury est favorable
            # (AAC / R1S / R2S) ou si le résultat compilé indique une promotion.
            if jury_decision in ("AAC", "R1S", "R2S") or is_promoted or compiled_status == "passed":
                return
            raise ValidationError(
                "Promotion refusée : aucune décision favorable (AAC/R1S/R2S) ou résultat validé ne permet le passage."
            )

        if mode == AnnualRegistrationService.REPEAT:
            # Pour le redoublement, autoriser la plupart des cas sauf si le jury
            # a explicitement indiqué réussite (R1S / R2S). On accepte aussi si
            # le résultat compilé indique 'repeat' ou 'failed'.
            if compiled_status in ["repeat", "failed"]:
                return
            if jury_decision in ("R1S", "R2S"):
                raise ValidationError("Redoublement refusé : décision du jury indique réussite.")
            # Tout le reste est autorisé (sauf AAA/ND qui sont bloqués plus haut).
            return

    @staticmethod
    def _validate_class_transition(source, target_class, mode):
        source_class = source.class_fk
        if not source_class:
            raise ValidationError("L'inscription source n'a pas de classe.")

        source_type = source_class.department.faculty.types
        target_type = target_class.department.faculty.types
        if source_type != target_type:
            raise ValidationError(
                "La réinscription annuelle ne change pas le type de formation. Utilisez le processus de remplacement/équivalence."
            )

        if mode == AnnualRegistrationService.PROMOTED:
            expected_level = source_class.level + 1
            if target_class.level != expected_level:
                raise ValidationError(
                    f"Promotion impossible : la classe cible doit être au niveau {expected_level}."
                )
        else:
            if target_class.level != source_class.level:
                raise ValidationError(
                    "Redoublement impossible : la classe cible doit être du même niveau que l'inscription source."
                )

        if target_class.level > 1 and target_class.department != source_class.department:
            started_first_year = Inscription.objects.filter(
                student=source.student,
                class_fk__department=target_class.department,
                class_fk__level=1,
                regist_status__in=["Active", "Completed", "Complement"],
            ).exists()
            if not started_first_year:
                raise ValidationError(
                    "Changement de département refusé : à partir de la deuxième année, "
                    "l'étudiant doit avoir commencé la première année dans ce département."
                )

    @staticmethod
    def _close_source_year(source, user):
        if source.regist_status in ["Active", "Pending", "Complement"]:
            update_data = {"regist_status": "Completed"}
            if user:
                update_data["modified_by"] = user
                update_data["modified_at"] = timezone.now()
            Inscription.objects.filter(pk=source.pk).update(**update_data)

    @staticmethod
    def _build_success_message(mode, target_academic_year:"AcademicYearType"):
        action = "Promotion" if mode == AnnualRegistrationService.PROMOTED else "Redoublement"
        message = f"{action} enregistré(e) avec succès pour {target_academic_year.academic_year}."
        if target_academic_year.is_closed:
            message += (
                " Attention : l'année académique cible est fermée, l'inscription "
                "sera conservée dans les archives de cette année."
            )
        message += " Les frais d'inscription restent dus pour cette nouvelle année académique."
        return message
