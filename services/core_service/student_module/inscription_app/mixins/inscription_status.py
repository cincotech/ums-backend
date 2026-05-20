"""
Mixin for inscription status transition methods.
"""
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from django.db import models


class InscriptionStatusMixin:
    """
    Mixin containing lightweight status transition methods.
    These methods are safe to call self.save() as they represent domain actions.
    """

    def activate(self, skip_payment_check=False):
        """
        Activate the inscription.
        
        Args:
            skip_payment_check: If True, skips payment verification (used by student_service)
        """
        from django.core.exceptions import ValidationError
        
        if self.regist_status in ["Pending", "Suspended"]:
            # Check payment before activation (skip if created by student_service)
            if not skip_payment_check and not self.has_verified_payment():
                raise ValidationError(
                    "Cannot activate inscription: Payment for inscription fees must be verified first. "
                )

            self.regist_status = "Active"

            # Assign Student role if user doesn't have it
            user = self.student.user
            if not user.role or user.role.name != "student":
                from services.foundational_service.auth_module.user_app.models import (
                    Role,
                )

                student_role, _ = Role.objects.get_or_create(name="student")
                user.role = student_role
                user.save(update_fields=["role"])

            self.save()

    def complete(self):
        """Mark inscription as completed."""
        if self.regist_status == "Active":
            self.regist_status = "Completed"
            self.save()

    def withdraw(self):
        """Withdraw the inscription."""
        if self.regist_status in ["Active", "Pending"]:
            self.regist_status = "Withdrawn"
            self.withdrawal_date = self._get_current_date()
            self.save()

    def drop(self):
        """Drop the inscription."""
        if self.regist_status == "Active":
            self.regist_status = "Dropped"
            self.save()

    def suspend(self):
        """Suspend the inscription."""
        if self.regist_status == "Active":
            self.regist_status = "Suspended"
            self.save()

    def cancel(self):
        """Cancel the inscription."""
        if self.regist_status in ["Pending", "Active"]:
            self.regist_status = "Canceled"
            self.save()

    def replace(self, new_class):
        """
        Replace a student's class/faculty safely:
        - Marks current inscription as 'Replaced'
        - Creates new inscription -> save() handles StudentMatricule generation
        - Never overwrites existing matricules
        - Checks se_mark eligibility for the new TypeFormation
        """
        from django.core.exceptions import ValidationError
        from django.db import transaction
        
        if self.regist_status not in ["Active", "Pending"]:
            raise ValidationError(
                "Only Active or Pending inscriptions can be replaced."
            )

        try:
            new_type = new_class.department.faculty.types
        except AttributeError:
            raise ValidationError(
                "Faculty type configuration is missing. Please contact the administrator."
            )

        self._validate_registration_eligibility(new_type)

        with transaction.atomic():
            self.__class__.objects.filter(pk=self.pk).update(regist_status="Replaced")

            new_inscription = self.__class__(
                student=self.student,
                academic_year=self.academic_year,
                class_fk=new_class,
                regist_status="Active",
                date_inscription=self.date_inscription,
            )
            new_inscription.save()
             
            # Transfer payment reference if needed
            # Note: In multi-inscription context, each inscription should have its own payment
            # The payment system should be updated to handle this properly

            return new_inscription

    def _get_current_date(self):
        """Helper to get current date."""
        from django.utils import timezone
        return timezone.now().date()