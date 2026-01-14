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

        # Créer un étudiant
        self.student = Student.objects.create(user=self.user, matricule="UMS2024001")

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
        print(f"✅ Étudiant : {reminder.student.matricule}")
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
            print(f"✅ Matricule : {student.matricule}")
            return True
        else:
            print("❌ Aucun étudiant trouvé")
            return False
    except Exception as e:
        print(f"❌ Erreur : {e}")
        return False
