"""
Service class for inscription automation logic (prepare and after_save phases).
"""

from typing import TYPE_CHECKING

from services.core_service.student_module.inscription_app.services.matricule_service import (
    MatriculeService,
)

if TYPE_CHECKING:
    from services.foundational_service.auth_module.user_app.models import User

    from .models import Inscription


class InscriptionAutomation:
    """
    Handles automation logic for inscription save operations.
    Split into prepare (pre-save mutation) and after_save (post-save side effects) phases.
    """

    @staticmethod
    def prepare(inscription: "Inscription", user: "User | None" = None) -> None:
        """
        PRE-SAVE Phase: Mutates instance safely BEFORE database save.

        Args:
            inscription: The inscription instance being saved
            user: The user performing the save operation (optional)
        """
        # Set created_by and modified_by before clean() to allow payment check skip
        if user:
            if inscription._state.adding:
                inscription.created_by = user
            inscription.modified_by = user
            from django.utils import timezone

            inscription.modified_at = timezone.now()

        # Auto-activate if created by student_service (no payment check)
        if (
            inscription._state.adding
            and user
            and hasattr(user, "role")
            and user.role
            and user.role.name == "student_service"
            and inscription.regist_status == "Pending"
        ):
            inscription.regist_status = "Active"

        # Also activate on update if still pending and user is student_service
        if (
            not inscription._state.adding
            and user
            and hasattr(user, "role")
            and user.role
            and user.role.name == "student_service"
            and inscription.regist_status == "Pending"
        ):
            inscription.regist_status = "Active"

        # Set class_group if not set and this is a new inscription
        if inscription._state.adding and inscription.class_group is None:
            inscription.class_group = (
                InscriptionAutomation._get_or_create_default_group(inscription)
            )

    @staticmethod
    def after_save(inscription: "Inscription", created: bool = False) -> None:
        """
        POST-SAVE Phase: Handles side effects AFTER successful persistence.

        Args:
            inscription: The inscription instance that was saved
            created: Boolean indicating if this was a new inscription
        """
        # Generate matricule for this TypeFormation if not yet created (only for new inscriptions)
        if created:
            try:
                type_formation = inscription.class_fk.department.faculty.types
                type_code = type_formation.code
            except AttributeError:
                type_code = "X"

            if type_code != "X":
                from services.core_service.student_module.student_profile_app.models import (
                    StudentMatricule,
                )

                has_matricule = StudentMatricule.objects.filter(
                    student=inscription.student, type_formation=type_formation
                ).exists()
                if not has_matricule:
                    # Use transaction to prevent race conditions in matricule generation
                    from django.db import transaction

                    year = inscription.academic_year.civil_year
                    with transaction.atomic():
                        new_matricule = MatriculeService._get_available_matricule(
                            type_code=type_code,
                            civil_year=year,
                        )
                        StudentMatricule.objects.create(
                            student=inscription.student,
                            type_formation=type_formation,
                            matricule=new_matricule,
                            academic_year=inscription.academic_year,
                        )

    @staticmethod
    def _get_or_create_default_group(inscription: "Inscription"):
        """
        Helper method to get or create default class group.
        """
        if not inscription.class_fk or not inscription.academic_year:
            return None

        from django.db import transaction

        from services.core_service.academic_module.class_app.models import ClassGroup

        with transaction.atomic():
            group, created = ClassGroup.objects.get_or_create(
                class_fk=inscription.class_fk,
                academic_year=inscription.academic_year,
                group_name="G1",
                defaults={"is_default": True},
            )

            if not group.is_default:
                group.is_default = True
                group.save(update_fields=["is_default"])

            return group
