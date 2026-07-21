"""
Centralized business validation rules for Inscription model.
"""

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .models import Inscription


class InscriptionValidator:
    """
    Centralized business validation rules.
    """

    @staticmethod
    def validate(inscription: "Inscription") -> None:
        """
        Validate all business rules for an inscription.

        Args:
            inscription: The inscription instance to validate

        Raises:
            ValidationError: If any business rule is violated
        """
        # Early return if required fields are missing
        if not inscription.student or not inscription.class_fk:
            return

        # 0️⃣ CHECK PAYMENT BEFORE ACTIVATION (skip if created by student_service)
        if inscription.regist_status == "Active" and inscription.pk:
            previous = inscription.__class__.objects.filter(pk=inscription.pk).first()
            if previous and previous.regist_status != "Active":
                # Skip payment check if created by student_service
                skip_payment = (
                    inscription.created_by
                    and hasattr(inscription.created_by, "role")
                    and inscription.created_by.role
                    and inscription.created_by.role.name == "student_service"
                )
                if not skip_payment and not inscription.has_verified_payment():
                    from django.core.exceptions import ValidationError

                    raise ValidationError(
                        "Impossible d'activer l'inscription : le paiement des frais d'inscription doit d'abord être vérifié."
                    )

        # 1️⃣ BLOCK FACULTY CHANGE VIA UPDATE
        if inscription.pk:
            previous = (
                inscription.__class__.objects.filter(pk=inscription.pk)
                .select_related("class_fk__department__faculty")
                .first()
            )

            if previous:
                old_faculty = previous.class_fk.department.faculty
                new_faculty = inscription.class_fk.department.faculty

                if old_faculty != new_faculty:
                    from django.core.exceptions import ValidationError

                    raise ValidationError(
                        "Le changement de faculté n'est pas autorisé lors de la mise à jour. "
                        "Si vous souhaitez déplacer l'étudiant vers une autre faculté, "
                        "utilisez le processus de remplacement."
                    )

            if previous and previous.class_fk != inscription.class_fk:
                same_faculty = (
                    previous.class_fk.department.faculty
                    == inscription.class_fk.department.faculty
                )
                if same_faculty and not previous.can_change_class:
                    from django.core.exceptions import ValidationError

                    raise ValidationError(
                        f"Impossible de déplacer l'étudiant vers une autre classe dans la même faculté. "
                        f"Statut actuel de l'inscription : '{previous.regist_status}'."
                    )

        # 2️⃣ MATRICULE TYPE VS FACULTY TYPE CHECK
        try:
            class_type_formation = inscription.class_fk.department.faculty.types
        except AttributeError:
            from django.core.exceptions import ValidationError

            raise ValidationError(
                "La configuration du type de faculté est manquante. Veuillez contacter l'administrateur."
            )

        # Check via StudentMatricule table (multi-matricule support)
        from services.core_service.student_module.student_profile_app.models import (
            StudentMatricule,
        )

        existing_matricule = (
            StudentMatricule.objects.filter(student=inscription.student)
            .exclude(type_formation=class_type_formation)
            .first()
        )

        if existing_matricule:
            # Student has a matricule for a different type — that's fine, multi-formation allowed
            # But if they already have one for THIS type, no conflict
            pass

        # Legacy check removed — Student.matricule field no longer exists.
        # Validation now relies solely on StudentMatricule entries.

        # 3️⃣ SINGLE ACTIVE/PENDING INSCRIPTION PER CLASS PER ACADEMIC YEAR
        # Updated: Allow multiple inscriptions in different classes of same level/department
        if not inscription.academic_year:
            return

        # Vérifier qu'il n'y a pas déjà une inscription pour cette classe spécifique
        qs = inscription.__class__.objects.filter(
            student=inscription.student,
            academic_year=inscription.academic_year,
            class_fk=inscription.class_fk,  # Même classe exacte
            regist_status__in=["Active", "Pending"],
        )

        if inscription.pk:
            qs = qs.exclude(pk=inscription.pk)

        if qs.exists():
            from django.core.exceptions import ValidationError

            raise ValidationError(
                "Cet étudiant a déjà une inscription active ou en attente pour cette classe spécifique dans l'année académique sélectionnée."
            )

        # 4️⃣ NO HIGHER LEVEL INSCRIPTION IN THE SAME ACADEMIC YEAR
        # Same TypeFormation, same level or higher → blocked
        # Exception: different department within the same faculty is allowed
        # (common years where students split into departments)
        target_type = inscription.class_fk.department.faculty.types
        target_level = inscription.class_fk.level
        target_department = inscription.class_fk.department
        target_class = inscription.class_fk
        # 🔒 1. Bloquer doublon exact (même classe)
        same_class = inscription.__class__.objects.filter(
            student=inscription.student,
            academic_year=inscription.academic_year,
            class_fk=target_class,
            regist_status__in=["Active", "Pending", "Completed"],
        )

        # 🔁 Exclure soi-même en update
        if inscription.pk:
            same_class = same_class.exclude(pk=inscription.pk)

        if same_class.exists():
            from django.core.exceptions import ValidationError

            raise ValidationError(
                "L'étudiant est déjà inscrit dans cette classe pour cette année académique."
            )

        same_year_higher = inscription.__class__.objects.filter(
            student=inscription.student,
            academic_year=inscription.academic_year,
            class_fk__level__gte=target_level,
            class_fk__department=target_department,  # 🎯 clé ici
            regist_status__in=["Active", "Pending", "Completed"],
        )

        # Exclure l'objet courant en cas de mise à jour
        if inscription.pk:
            same_year_higher = same_year_higher.exclude(pk=inscription.pk)

        if same_year_higher.exists():
            from django.core.exceptions import ValidationError

            raise ValidationError(
                f"L'étudiant a déjà une inscription au niveau {target_level} ou supérieur dans ce département pour cette année académique."
            )

        # 5️⃣ NO LEVEL SKIP — must have completed previous level
        if target_level > 1:
            # Exception: student comes from another university
            # graduate_infos must match the same TypeFormation as the target class
            has_university_background = inscription.student.graduate_infos.filter(
                department__faculty__types=target_type
            ).exists()

            if not has_university_background:
                previous_level_done = inscription.__class__.objects.filter(
                    student=inscription.student,
                    class_fk__level=target_level - 1,
                    class_fk__department__faculty__types=target_type,
                    regist_status__in=["Active", "Completed", "Complement"],
                ).exists()

                if not previous_level_done:
                    from django.core.exceptions import ValidationError

                    raise ValidationError(
                        f"L'étudiant n'a pas d'inscription au niveau {target_level - 1} dans le même type de formation. "
                        f"Impossible de s'inscrire au niveau {target_level} sans avoir complété le niveau précédent. "
                        f"Si l'étudiant vient d'une autre université, veuillez d'abord renseigner les informations sur le parcours universitaire."
                    )

        # 6 - REGISTRATION ELIGIBILITY
        # Highschool drives F/I baseline admission. University parcours can
        # override highschool only for advanced tracks such as Master/Doctorate.
        inscription._validate_registration_eligibility(target_type)
