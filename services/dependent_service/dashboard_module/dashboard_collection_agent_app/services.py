# from datetime import timedelta
# from decimal import Decimal

# from django.db.models import Sum
# from django.utils import timezone

# # from services.core_service.finance_module.fees_app.models import FeesSheet
# # from services.core_service.finance_module.payment_app.models import Payment
# from services.core_service.student_module.student_profile_app.models import Student

# from .models import (
#     CollectionCorrespondence,
#     PaymentPlan,
#     PaymentPromise,
#     PaymentReminder,
# )


# class CollectionAgentService:

#     @staticmethod
#     def get_dashboard_stats():
#         """Get collection agent dashboard overview"""

#         # Calculate total debt and debtors
#         total_fees = FeesSheet.objects.aggregate(total=Sum("base_amount"))[
#             "total"
#         ] or Decimal("0")
#         total_payments = Payment.objects.filter(payment_status="verified").aggregate(
#             total=Sum("amount_paid")
#         )["total"] or Decimal("0")
#         total_debt = total_fees - total_payments

#         # Count debtors (students with outstanding balances)
#         debtors_list = CollectionAgentService.get_debtors_list()
#         debtors = len(debtors_list)

#         # Count overdue cases (students with unpaid installments past deadline)
#         timezone.now().date()
#         overdue_count = 0
#         for debtor in debtors_list:
#             if debtor.get("days_overdue", 0) > 0:
#                 overdue_count += 1

#         active_plans = PaymentPlan.objects.filter(status="active").count()
#         pending_promises = PaymentPromise.objects.filter(status="pending").count()
#         legal_cases = LegalCase.objects.filter(
#             status__in=["prepared", "submitted", "in_progress"]
#         ).count()

#         return {
#             "total_debtors": debtors,
#             "total_debt_amount": float(total_debt),
#             "overdue_cases": overdue_count,
#             "active_payment_plans": active_plans,
#             "pending_promises": pending_promises,
#             "legal_cases": legal_cases,
#         }

#     @staticmethod
#     def get_debtors_list(filters=None):
#         """Get list of students with outstanding debts

#         Args:
#             filters: Optional dict with keys:
#                 - program: Filter by program name
#                 - academic_year: Filter by academic year ID
#                 - min_amount: Minimum debt amount
#                 - min_days_overdue: Minimum days overdue

#         Returns:
#             List of dicts with debtor information
#         """
#         from datetime import datetime

#         from services.core_service.student_module.inscription_app.models import (
#             Inscription,
#         )

#         # Get all active inscriptions
#         inscriptions = Inscription.objects.filter(regist_status="ACT").select_related(
#             "student", "student__user", "academic_year", "class_fk"
#         )

#         debtor_data = []
#         today = timezone.now().date()

#         for inscription in inscriptions:
#             student = inscription.student

#             # Get fees sheet for this inscription
#             try:
#                 fees_sheet = FeesSheet.objects.get(
#                     class_fk=inscription.class_fk,
#                     academic_year=inscription.academic_year,
#                 )
#             except FeesSheet.DoesNotExist:
#                 continue

#             # Calculate total paid
#             total_paid = Payment.objects.filter(
#                 inscription=inscription, payment_status="verified"
#             ).aggregate(total=Sum("amount_paid"))["total"] or Decimal("0")

#             total_required = Decimal(fees_sheet.base_amount)
#             debt = total_required - total_paid

#             if debt > Decimal("0"):  # Only include students with debt
#                 # Calculate what should be paid by now based on installments
#                 installments = fees_sheet.installements or []
#                 required_by_now = Decimal("0")
#                 overdue_amount = Decimal("0")
#                 days_overdue = 0

#                 if installments:
#                     for installment in installments:
#                         deadline = installment.get("deadline")
#                         if deadline:
#                             deadline_date = datetime.fromisoformat(str(deadline)).date()
#                             if deadline_date <= today:
#                                 required_by_now += Decimal(
#                                     str(installment.get("amount", 0))
#                                 )

#                     overdue_amount = max(Decimal("0"), required_by_now - total_paid)

#                     # Find earliest overdue deadline
#                     for installment in installments:
#                         deadline = installment.get("deadline")
#                         if deadline:
#                             deadline_date = datetime.fromisoformat(str(deadline)).date()
#                             if deadline_date <= today:
#                                 amount_for_deadline = Decimal(
#                                     str(installment.get("amount", 0))
#                                 )
#                                 if total_paid < amount_for_deadline:
#                                     days_overdue = (today - deadline_date).days
#                                     break
#                 else:
#                     # No installments, entire amount is overdue if past end of semester
#                     overdue_amount = debt

#                 debtor_data.append(
#                     {
#                         "student_id": str(student.id),
#                         "matricule": student.matricule,
#                         "full_name": f"{student.user.first_name} {student.user.last_name}",
#                         "email": student.user.email,
#                         "phone": student.user.phone_number or "",
#                         "program": (
#                             inscription.class_fk.department.name
#                             if inscription.class_fk and inscription.class_fk.department
#                             else "N/A"
#                         ),
#                         "academic_year": str(inscription.academic_year),
#                         "total_required": float(total_required),
#                         "total_paid": float(total_paid),
#                         "total_debt": float(debt),
#                         "required_by_now": float(required_by_now),
#                         "overdue_amount": float(overdue_amount),
#                         "days_overdue": days_overdue,
#                     }
#                 )

#         # Apply filters if provided
#         if filters:
#             if filters.get("program"):
#                 debtor_data = [
#                     d for d in debtor_data if filters["program"] in d["program"]
#                 ]

#             if filters.get("academic_year"):
#                 debtor_data = [
#                     d
#                     for d in debtor_data
#                     if filters["academic_year"] in d["academic_year"]
#                 ]

#             if filters.get("min_amount"):
#                 min_amount = float(filters["min_amount"])
#                 debtor_data = [d for d in debtor_data if d["total_debt"] >= min_amount]

#             if filters.get("min_days_overdue"):
#                 min_days = int(filters["min_days_overdue"])
#                 debtor_data = [d for d in debtor_data if d["days_overdue"] >= min_days]

#         # Sort by days overdue (descending) then by debt amount (descending)
#         debtor_data.sort(
#             key=lambda x: (x["days_overdue"], x["total_debt"]), reverse=True
#         )

#         return debtor_data

#     @staticmethod
#     def extract_debtor_data(filters=None):
#         """Alias for get_debtors_list for backwards compatibility"""
#         return CollectionAgentService.get_debtors_list(filters)

#     @staticmethod
#     def record_payment(student_id, amount, payment_method, reference, user):
#         """Record payment and update status"""
#         payment = Payment.objects.create(
#             student_id=student_id,
#             amount_paid=amount,
#             payment_method=payment_method,
#             reference=reference,
#             payment_date=timezone.now().date(),
#         )

#         # Update installment status if applicable
#         overdue_installments = Payment.objects.filter(
#             student_id=student_id, status__in=["pending", "overdue"]
#         ).order_by("due_date")

#         remaining_amount = amount
#         for installment in overdue_installments:
#             if remaining_amount <= 0:
#                 break

#             if remaining_amount >= installment.amount:
#                 installment.paid_amount = installment.amount
#                 installment.status = "paid"
#                 installment.paid_date = timezone.now().date()
#                 remaining_amount -= installment.amount
#             else:
#                 installment.paid_amount += remaining_amount
#                 remaining_amount = 0

#             installment.save()

#         return payment

#     @staticmethod
#     def send_reminder(student_id, reminder_type, user):
#         """Send payment reminder to student"""
#         from services.dependent_service.dashboard_module.dashboard_shared_app.models import (
#             Notification,
#         )

#         student = Student.objects.get(id=student_id)

#         # Calculate amount due
#         total_debt = CollectionAgentService._calculate_student_debt(student)

#         # Generate message based on reminder type
#         messages = {
#             "reminder_7": f"Rappel: Votre paiement de {total_debt} est en retard depuis 7 jours.",
#             "reminder_30": f"Relance: Votre dette de {total_debt} doit être réglée immédiatement.",
#             "formal_notice_60": f"Mise en demeure: Réglez votre dette de {total_debt} sous 15 jours.",
#             "final_notice": f"Dernier avis: Procédure judiciaire engagée pour {total_debt}.",
#         }

#         message = messages.get(reminder_type, "Rappel de paiement")

#         reminder = PaymentReminder.objects.create(
#             student=student,
#             reminder_type=reminder_type,
#             amount_due=total_debt,
#             message=message,
#             sent_by=user,
#             status="sent",
#         )

#         # Create in-app notification for student
#         Notification.objects.create(
#             recipient=student.user,
#             recipient_type="student",
#             notification_type="payment_reminder",
#             title=f"Rappel de Paiement - {reminder_type}",
#             message=message,
#         )

#         return reminder

#     @staticmethod
#     def send_automatic_reminders(user):
#         """Automatically send reminders to students based on overdue days

#         This method should be called periodically (e.g., via cron job or celery task)
#         to send automatic reminders to students with overdue payments.

#         Reminder schedule:
#         - 7 days overdue: First reminder
#         - 30 days overdue: Second reminder (relance)
#         - 60 days overdue: Formal notice (mise en demeure)
#         - 90+ days overdue: Final notice before legal action

#         Args:
#             user: User object (system user for automated reminders)

#         Returns:
#             dict with counts of reminders sent
#         """

#         debtors = CollectionAgentService.get_debtors_list()
#         reminders_sent = {
#             "reminder_7": 0,
#             "reminder_30": 0,
#             "formal_notice_60": 0,
#             "final_notice": 0,
#         }

#         for debtor in debtors:
#             days_overdue = debtor.get("days_overdue", 0)
#             student_id = debtor.get("student_id")

#             if days_overdue <= 0:
#                 continue

#             # Get student
#             try:
#                 student = Student.objects.get(id=student_id)
#             except Student.DoesNotExist:
#                 continue

#             # Check if reminder was already sent recently (within 7 days)
#             recent_reminders = PaymentReminder.objects.filter(
#                 student=student, sent_at__gte=timezone.now() - timedelta(days=7)
#             ).exists()

#             if recent_reminders:
#                 continue  # Don't spam with reminders

#             # Determine reminder type based on days overdue
#             reminder_type = None
#             if days_overdue >= 90:
#                 reminder_type = "final_notice"
#             elif days_overdue >= 60:
#                 reminder_type = "formal_notice_60"
#             elif days_overdue >= 30:
#                 reminder_type = "reminder_30"
#             elif days_overdue >= 7:
#                 reminder_type = "reminder_7"

#             if reminder_type:
#                 # Send reminder
#                 try:
#                     CollectionAgentService.send_reminder(
#                         student_id, reminder_type, user
#                     )
#                     reminders_sent[reminder_type] += 1
#                 except Exception as e:
#                     # Log error but continue with other reminders
#                     print(f"Error sending reminder to student {student_id}: {e}")
#                     continue

#         return {
#             "total_reminders_sent": sum(reminders_sent.values()),
#             "reminders_by_type": reminders_sent,
#         }

#     @staticmethod
#     def create_payment_plan(student_id, total_amount, monthly_amount, start_date, user):
#         """Create payment plan for student"""
#         # Calculate end date based on monthly amount
#         months = int(total_amount / monthly_amount)
#         end_date = start_date + timedelta(days=months * 30)

#         plan = PaymentPlan.objects.create(
#             student_id=student_id,
#             total_amount=total_amount,
#             monthly_amount=monthly_amount,
#             start_date=start_date,
#             end_date=end_date,
#             created_by=user,
#         )

#         # Create installments
#         current_date = start_date
#         for i in range(months):
#             Payment.objects.create(
#                 student_id=student_id,
#                 amount=monthly_amount,
#                 due_date=current_date,
#                 created_by=user,
#             )
#             current_date += timedelta(days=30)

#         return plan

#     @staticmethod
#     def record_payment_promise(student_id, amount, promised_date, notes, user):
#         """Record payment promise from student"""
#         promise = PaymentPromise.objects.create(
#             student_id=student_id,
#             promised_amount=amount,
#             promised_date=promised_date,
#             notes=notes,
#             recorded_by=user,
#         )

#         return promise

#     @staticmethod
#     def send_correspondence(student_id, correspondence_type, subject, content, user):
#         """Send correspondence to student"""
#         correspondence = CollectionCorrespondence.objects.create(
#             student_id=student_id,
#             correspondence_type=correspondence_type,
#             subject=subject,
#             content=content,
#             sent_by=user,
#         )

#         return correspondence

#     @staticmethod
#     def prepare_legal_case(student_id, user):
#         """Prepare legal case for irrecoverable debt"""
#         student = Student.objects.get(id=student_id)
#         total_debt = CollectionAgentService._calculate_student_debt(student)

#         # Gather case documents
#         documents = []

#         # Payment history
#         payments = Payment.objects.filter(student=student)
#         documents.append(
#             {
#                 "type": "payment_history",
#                 "data": [
#                     {"amount": p.amount_paid, "date": p.payment_date.isoformat()}
#                     for p in payments
#                 ],
#             }
#         )

#         # Correspondence history
#         correspondence = CollectionCorrespondence.objects.filter(student=student)
#         documents.append(
#             {
#                 "type": "correspondence",
#                 "data": [
#                     {"type": c.correspondence_type, "date": c.sent_at.isoformat()}
#                     for c in correspondence
#                 ],
#             }
#         )

#         # Reminders sent
#         reminders = PaymentReminder.objects.filter(student=student)
#         documents.append(
#             {
#                 "type": "reminders",
#                 "data": [
#                     {"type": r.reminder_type, "date": r.sent_at.isoformat()}
#                     for r in reminders
#                 ],
#             }
#         )

#         legal_case = LegalCase.objects.create(
#             student=student,
#             total_debt=total_debt,
#             case_documents=documents,
#             prepared_by=user,
#         )

#         return legal_case

#     @staticmethod
#     def update_installment_due_date(installment_id, new_due_date, user):
#         """Update installment due date for justified cases"""
#         installment = Payment.objects.get(id=installment_id)
#         installment.due_date = new_due_date
#         installment.save()

#         return installment

#     @staticmethod
#     def _calculate_student_debt(student):
#         """Calculate total debt for a student across all active inscriptions"""
#         from services.core_service.student_module.inscription_app.models import (
#             Inscription,
#         )

#         # Get active inscriptions
#         inscriptions = Inscription.objects.filter(student=student, regist_status="ACT")

#         total_debt = Decimal("0")

#         for inscription in inscriptions:
#             # Get fees sheet
#             try:
#                 fees_sheet = FeesSheet.objects.get(
#                     class_fk=inscription.class_fk,
#                     academic_year=inscription.academic_year,
#                 )

#                 # Calculate paid amount
#                 total_paid = Payment.objects.filter(
#                     inscription=inscription, payment_status="verified"
#                 ).aggregate(total=Sum("amount_paid"))["total"] or Decimal("0")

#                 debt = Decimal(fees_sheet.base_amount) - total_paid
#                 total_debt += max(Decimal("0"), debt)

#             except FeesSheet.DoesNotExist:
#                 continue

#         return total_debt
