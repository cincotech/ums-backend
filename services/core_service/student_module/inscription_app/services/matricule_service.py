"""
Service class for matricule generation and management.
"""

from typing import TYPE_CHECKING

if TYPE_CHECKING:

    from .models import Inscription


class MatriculeService:
    """
    Stateless service class for matricule operations.
    """

    @staticmethod
    def generate_for_inscription(inscription: "Inscription") -> str | None:
        """
        Generates and assigns a matricule per TypeFormation.
        Returns the existing one if already generated for this type.
        Format: {TypeCode}{civil_year}/{00001}
        """
        from services.core_service.student_module.student_profile_app.models import (
            StudentMatricule,
        )

        try:
            type_formation = inscription.class_fk.department.faculty.types
            type_code = type_formation.code
        except AttributeError:
            type_code = "X"
            return None

        # Return existing matricule for this type if already exists
        existing = StudentMatricule.objects.filter(
            student=inscription.student, type_formation=type_formation
        ).first()
        if existing:
            return existing.matricule

        year = inscription.academic_year.civil_year

        # Use transaction to prevent race conditions
        from django.db import transaction

        with transaction.atomic():
            matricule = MatriculeService._get_available_matricule(
                type_code=type_code,
                civil_year=year,
            )

            StudentMatricule.objects.create(
                student=inscription.student,
                type_formation=type_formation,
                matricule=matricule,
                academic_year=inscription.academic_year,
            )

        return matricule

    @staticmethod
    def _get_available_matricule(
        type_code: str,
        civil_year: int,
        preferred_number: int | None = None,
        exclude_matricule_id: int | None = None,
    ) -> str:
        """
        Get an available matricule number for the given type and year.
        """
        import re

        from services.core_service.student_module.student_profile_app.models import (
            StudentMatricule,
        )

        prefix = f"{type_code}{civil_year}/"
        existing_qs = StudentMatricule.objects.select_for_update().filter(
            matricule__startswith=prefix
        )
        if exclude_matricule_id:
            existing_qs = existing_qs.exclude(pk=exclude_matricule_id)

        used_numbers = set()
        for existing in existing_qs.values_list("matricule", flat=True):
            match = re.search(r"/(\d+)$", existing or "")
            if match:
                number = int(match.group(1))
                if number is not None:
                    used_numbers.add(number)

        if preferred_number and preferred_number not in used_numbers:
            return f"{prefix}{str(preferred_number).zfill(5)}"

        next_number = max(used_numbers, default=0) + 1
        while next_number in used_numbers:
            next_number += 1

        return f"{prefix}{str(next_number).zfill(5)}"

    @staticmethod
    def _extract_matricule_number(matricule: str) -> int | None:
        """
        Extract the numeric part from a matricule string.
        """
        import re

        match = re.search(r"/(\d+)$", matricule or "")
        return int(match.group(1)) if match else None

    @staticmethod
    def transfer_academic_year(
        inscription: "Inscription", target_academic_year, user=None
    ):
        """
        Move this inscription to another academic year atomically.

        This is intentionally different from a plain PATCH because the class group
        depends on the academic year. When the year changes, the inscription must
        be attached to the default group for the same class in the target year.
        and the matricule must be updated if it includes the year. This method ensures
        atomicity of the operation.
        """
        if inscription.academic_year_id == target_academic_year.id:
            return inscription

        from django.db import transaction

        with transaction.atomic():
            inscription_obj = (
                inscription.__class__.objects.select_for_update()
                .select_related(
                    "academic_year",
                    "class_fk__department__faculty__types",
                    "student",
                )
                .get(pk=inscription.pk)
            )
            old_academic_year = inscription_obj.academic_year
            inscription_obj.academic_year = target_academic_year
            inscription_obj.class_group = inscription_obj.get_or_create_default_group()

            if user:
                inscription_obj.modified_by = user
                from django.utils import timezone

                inscription_obj.modified_at = timezone.now()

            inscription_obj.clean()

            update_fields = ["academic_year", "class_group"]
            if user:
                update_fields.extend(["modified_by", "modified_at"])
            super(inscription.__class__, inscription_obj).save(
                update_fields=update_fields
            )

            inscription_obj._transfer_matricule_year_if_needed(old_academic_year)

            return inscription_obj

    @staticmethod
    def _transfer_matricule_year_if_needed(
        inscription: "Inscription", old_academic_year
    ):
        """
        Keep the student's TypeFormation matricule coherent when an inscription
        was created in the wrong year and is corrected before another inscription
        uses that old-year matricule.
        """
        try:
            type_formation = inscription.class_fk.department.faculty.types
            type_code = type_formation.code
        except AttributeError:
            return

        from services.core_service.student_module.student_profile_app.models import (
            StudentMatricule,
        )

        matricule = (
            StudentMatricule.objects.select_for_update()
            .filter(
                student=inscription.student,
                type_formation=type_formation,
                academic_year=old_academic_year,
            )
            .first()
        )
        if not matricule:
            return

        old_year_still_used = (
            inscription.__class__.objects.filter(
                student=inscription.student,
                academic_year=old_academic_year,
                class_fk__department__faculty__types=type_formation,
            )
            .exclude(pk=inscription.pk)
            .exists()
        )
        if old_year_still_used:
            return

        old_prefix = f"{type_code}{old_academic_year.civil_year}/"
        if matricule.matricule.startswith(old_prefix):
            preferred_number = MatriculeService._extract_matricule_number(
                matricule.matricule
            )
            matricule.matricule = MatriculeService._get_available_matricule(
                type_code=type_code,
                civil_year=inscription.academic_year.civil_year,
                preferred_number=preferred_number,
                exclude_matricule_id=matricule.pk,
            )

        matricule.academic_year = inscription.academic_year
        matricule.save(update_fields=["academic_year", "matricule"])

    @staticmethod
    def get_or_create_default_group(inscription: "Inscription"):
        """
        Returns the default class group (G1) for this inscription's class and academic year.
        Creates it if it does not exist, and ensures it is marked as default.
        """
        if not inscription.class_fk or not inscription.academic_year:
            return None

        from django.db import transaction

        from services.core_service.academic_module.class_app.models import ClassGroup

        with transaction.atomic():
            group, _ = ClassGroup.objects.get_or_create(
                class_fk=inscription.class_fk,
                academic_year=inscription.academic_year,
                group_name="G1",
                defaults={"is_default": True},
            )

            if not group.is_default:
                group.is_default = True
                group.save(update_fields=["is_default"])

            return group
