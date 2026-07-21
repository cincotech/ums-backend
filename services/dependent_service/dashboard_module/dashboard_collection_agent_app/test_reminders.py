from django.core import mail
from django.test import TestCase

from .models import PaymentReminder, Student, User
from .services import NotificationService


class PaymentReminderTest(TestCase):

    def setUp(self):
        # Créer un utilisateur étudiant
        self.user = User.objects.create(
            email="test.student@ums.edu", first_name="Jean", last_name="Dupont"
        )

        # Créer un étudiant (sans champ matricule)
        self.student = Student.objects.create(user=self.user)

        # Créer un StudentMatricule pour l'étudiant
        from services.core_service.academic_module.faculty_app.models import (
            TypeFormation,
        )
        from services.core_service.academic_module.university_app.models import (
            AcademicYear,
        )
        from services.core_service.student_module.student_profile_app.models import (
            StudentMatricule,
        )

        # Créer les objets nécessaires
        type_formation = TypeFormation.objects.create(name="Faculté", code="F")
        academic_year = AcademicYear.objects.create(
            academic_year="2024-2025",
            civil_year="2025",
            start_date="2024-09-01",
            end_date="2025-07-31",
        )
        StudentMatricule.objects.create(
            student=self.student,
            type_formation=type_formation,
            matricule="UMS2024001",
            academic_year=academic_year,
        )

    def test_email_sending(self):
        """Test l'envoi d'email de rappel"""
        # Créer un rappel
        reminder = PaymentReminder.objects.create(
            student=self.student,
            reminder_type="reminder_7",
            amount_due=500.00,
            message="Test de rappel de paiement",
            sent_by=self.user,
        )

        # Envoyer le rappel
        NotificationService.send_payment_reminder(reminder)

        # Vérifier qu'un email a été envoyé
        self.assertEqual(len(mail.outbox), 1)
        self.assertEqual(mail.outbox[0].to, ["test.student@ums.edu"])
        self.assertIn("Rappel de paiement", mail.outbox[0].subject)

    def test_email_path(self):
        """Test le chemin d'accès à l'email"""
        # Vérifier la chaîne : reminder → student → user → email
        reminder = PaymentReminder.objects.create(
            student=self.student,
            reminder_type="reminder_7",
            amount_due=500.00,
            message="Test",
            sent_by=self.user,
        )

        # Tester le chemin
        email = reminder.student.user.email
        self.assertEqual(email, "test.student@ums.edu")

        print(f"✅ Email trouvé : {email}")
        active_sm = reminder.student.get_active_matricule()
        print(f"✅ Étudiant : {active_sm.matricule if active_sm else 'No matricule'}")
        print(f"✅ Nom complet : {reminder.student.user.get_full_name()}")


# Pour tester manuellement :
def test_email_access():
    """Test manuel pour vérifier l'accès à l'email"""
    try:
        # Récupérer un étudiant existant
        student = Student.objects.first()
        if student:
            email = student.user.email
            print(f"✅ Email trouvé : {email}")
            active_sm = student.get_active_matricule()
            print(f"✅ Matricule : {active_sm.matricule if active_sm else 'Aucun'}")
            return True
        else:
            print("❌ Aucun étudiant trouvé")
            return False
    except Exception as e:
        print(f"❌ Erreur : {e}")
        return False
