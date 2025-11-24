# from decimal import Decimal

# from django.db.models import Count, Sum
# from django.utils import timezone

# from services.core_service.academic_module.teacher_app.models import Attribution
# from services.core_service.finance_module.fees_app.models import FeesSheet
# from services.core_service.finance_module.payment_app.models import Payment
# from services.core_service.student_module.student_profile_app.models import Student
# from services.dependent_service.exam_module.result_app.models import CompiledResult

# from .models import PaymentDerogation, RecteurDecision


# class RecteurDashboardService:

#     @staticmethod
#     def get_dashboard_stats():
#         """Get recteur dashboard overview statistics"""
#         pending_derogations = PaymentDerogation.objects.filter(status="pending").count()
#         pending_attributions = Attribution.objects.filter(
#             status_principal_teacher="Pending"
#         ).count()

#         # Payment statistics
#         total_payments = Payment.objects.aggregate(total=Sum("amount_paid"))[
#             "total"
#         ] or Decimal("0")

#         total_fees = FeesSheet.objects.aggregate(total=Sum("amount"))[
#             "total"
#         ] or Decimal("1")

#         collection_rate = (
#             float(total_payments / total_fees * 100) if total_fees > 0 else 0
#         )

#         # Academic performance
#         total_students = Student.objects.count()
#         passed_students = CompiledResult.objects.filter(status="passed").count()
#         success_rate = (
#             (passed_students / total_students * 100) if total_students > 0 else 0
#         )

#         return {
#             "pending_derogations": pending_derogations,
#             "pending_attributions": pending_attributions,
#             "total_payments_collected": total_payments,
#             "payment_collection_rate": round(collection_rate, 2),
#             "academic_success_rate": round(success_rate, 2),
#             "total_students": total_students,
#         }

#     @staticmethod
#     def get_payment_derogations(status=None):
#         """Get payment derogation requests"""
#         queryset = PaymentDerogation.objects.select_related(
#             "student__user", "requested_by"
#         )
#         if status:
#             queryset = queryset.filter(status=status)
#         return queryset.order_by("-created_at")

#     @staticmethod
#     def process_derogation(derogation_id, decision, notes, recteur_user):
#         """Process payment derogation decision"""
#         derogation = PaymentDerogation.objects.get(id=derogation_id)
#         derogation.status = decision
#         derogation.decision_notes = notes
#         derogation.reviewed_by = recteur_user
#         derogation.reviewed_at = timezone.now()
#         derogation.save()

#         # Record decision
#         RecteurDecision.objects.create(
#             decision_type="payment_derogation",
#             reference_id=str(derogation_id),
#             decision=decision,
#             notes=notes,
#             decided_by=recteur_user,
#         )

#         return derogation

#     @staticmethod
#     def get_visiting_professor_attributions():
#         """Get course attributions for visiting professors pending validation"""
#         return Attribution.objects.filter(
#             status_principal_teacher="Pending"
#         ).select_related("course", "principal_teacher__user", "academic_year")

#     @staticmethod
#     def validate_course_attribution(attribution_id, decision, notes, recteur_user):
#         """Validate course attribution for visiting professor"""
#         attribution = Attribution.objects.get(id=attribution_id)

#         if decision == "approved":
#             attribution.status_principal_teacher = "Accepted"
#         else:
#             attribution.status_principal_teacher = "Refused"

#         attribution.commentaire = notes
#         attribution.authorized_by = recteur_user
#         attribution.save()

#         # Record decision
#         RecteurDecision.objects.create(
#             decision_type="course_attribution",
#             reference_id=str(attribution_id),
#             decision=decision,
#             notes=notes,
#             decided_by=recteur_user,
#         )

#         return attribution

#     @staticmethod
#     def get_payment_overview():
#         """Get global payment tracking overview"""
#         total_fees = FeesSheet.objects.aggregate(total=Sum("amount"))[
#             "total"
#         ] or Decimal("0")
#         total_payments = Payment.objects.aggregate(total=Sum("amount_paid"))[
#             "total"
#         ] or Decimal("0")

#         collection_rate = (
#             float(total_payments / total_fees * 100) if total_fees > 0 else 0
#         )
#         outstanding = total_fees - total_payments

#         # Students with payment arrears
#         students_with_arrears = Student.objects.filter(
#             # This would need proper logic based on your payment structure
#             # For now, simplified version
#         ).count()

#         return {
#             "total_expected": total_fees,
#             "total_collected": total_payments,
#             "collection_rate": round(collection_rate, 2),
#             "outstanding_amount": outstanding,
#             "students_with_arrears": students_with_arrears,
#         }

#     @staticmethod
#     def get_academic_performance_overview():
#         """Get academic performance supervision data"""
#         total_students = Student.objects.count()

#         # Success rates by status
#         results_summary = CompiledResult.objects.values("status").annotate(
#             count=Count("id")
#         )

#         # Retention rate calculation
#         current_year_students = Student.objects.filter(
#             # Add logic for current academic year filtering
#         ).count()

#         retention_rate = (
#             (current_year_students / total_students * 100) if total_students > 0 else 0
#         )

#         return {
#             "total_students": total_students,
#             "results_breakdown": list(results_summary),
#             "retention_rate": round(retention_rate, 2),
#         }

#     @staticmethod
#     def get_quality_reports_summary():
#         """Get quality assurance reports summary for recteur review"""
#         from services.dependent_service.dashboard_module.dashboard_app.models import (
#             QualityReport,
#         )

#         recent_reports = QualityReport.objects.filter(
#             generated_date__gte=timezone.now().replace(day=1)  # This month
#         ).order_by("-generated_date")

#         return recent_reports
