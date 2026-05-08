from datetime import date, datetime

from django.db.models import Count, Q, Sum
from django.db.models.functions import Coalesce, TruncDay, TruncMonth, TruncWeek
from django.utils import timezone

from services.core_service.academic_module.university_app.models import AcademicYear
from services.dependent_service.infrastructure_module.building_app.models import (
    Building,
)
from services.dependent_service.infrastructure_module.equipment_app.models import (
    Equipment,
    EquipmentAllocation,
)
from services.dependent_service.infrastructure_module.room_app.models import Room

from .models import Payment, PaymentInstallement


class FinanceDashboardService:
    @staticmethod
    def _parse_date(value):
        if not value:
            return None
        if isinstance(value, date):
            return value
        try:
            return datetime.fromisoformat(value).date()
        except (TypeError, ValueError):
            return None

    @staticmethod
    def _normalize_period(period):
        period = (period or "monthly").lower()
        if period not in {"daily", "weekly", "monthly"}:
            return "monthly"
        return period

    @staticmethod
    def _get_trunc(period, field_name):
        if period == "daily":
            return TruncDay(field_name)
        if period == "weekly":
            return TruncWeek(field_name)
        return TruncMonth(field_name)

    @staticmethod
    def _format_period_label(period, period_value):
        if not period_value:
            return "-"
        if period == "daily":
            return period_value.strftime("%Y-%m-%d")
        if period == "weekly":
            # Represent week by its starting date
            return period_value.strftime("%Y-%m-%d")
        return period_value.strftime("%Y-%m")

    @staticmethod
    def _empty_payload(academic_year=None):
        return {
            "academic_year": academic_year,
            "kpis": {
                "total_expected": 0,
                "total_collected": 0,
                "outstanding": 0,
                "recovery_rate": 0,
                "overdue_installments_count": 0,
                "pending_payments_amount": 0,
                "verified_payments_count": 0,
                "unverified_payments_count": 0,
            },
            "trends": {
                "period": "monthly",
                "monthly_collections": [],
                "monthly_expected": [],
                "monthly_summary": [],
                "monthly_outstanding": [],
                "monthly_recovery_rate": [],
                "cumulative_collections": [],
            },
            "breakdowns": {"by_faculty": [], "by_payment_method": []},
            "recent_payments": [],
            "assets": {
                "buildings_count": 0,
                "rooms_count": 0,
                "rooms_available_count": 0,
                "rooms_by_type": [],
                "equipment_total": 0,
                "equipment_by_status": [],
                "equipment_under_maintenance_count": 0,
                "equipment_allocations_active_count": 0,
            },
        }

    @staticmethod
    def _get_academic_year(university, academic_year_id=None):
        if academic_year_id:
            ay = AcademicYear.objects.filter(id=academic_year_id).first()
            if not ay:
                return None
            # If academic year is linked to a university, enforce matching.
            if ay.university_id and university and ay.university_id != university.id:
                return None
            return ay

        today = timezone.now().date()
        active = AcademicYear.objects.filter(
            university=university,
            is_closed=False,
            start_date__lte=today,
            end_date__gte=today,
        ).first()
        if active:
            return active

        fallback = (
            AcademicYear.objects.filter(university=university)
            .order_by("-start_date")
            .first()
        )
        if fallback:
            return fallback

        # Legacy data fallback: academic years without university
        return (
            AcademicYear.objects.filter(university__isnull=True)
            .order_by("-start_date")
            .first()
        )

    @staticmethod
    def get_overview(
        university,
        academic_year_id=None,
        period=None,
        date_from=None,
        date_to=None,
    ):
        academic_year = FinanceDashboardService._get_academic_year(
            university, academic_year_id
        )

        if not academic_year:
            return FinanceDashboardService._empty_payload()

        period = FinanceDashboardService._normalize_period(period)
        date_from = FinanceDashboardService._parse_date(date_from)
        date_to = FinanceDashboardService._parse_date(date_to)

        payments_qs = Payment.objects.filter(
            Q(inscription__academic_year=academic_year)
            | Q(paymentplan__feessheet__academic_year=academic_year)
        ).select_related(
            "paymentplan__feessheet__class_fk__department__faculty",
            "paymentplan__feessheet__department__faculty",
            "paymentplan__feessheet__faculty",
            "inscription__student__user",
        )

        installments_qs = PaymentInstallement.objects.filter(
            payment_plan__feessheet__academic_year=academic_year
        ).select_related(
            "payment_plan__feessheet__class_fk__department__faculty",
            "payment_plan__feessheet__department__faculty",
            "payment_plan__feessheet__faculty",
        )

        if date_from:
            payments_qs = payments_qs.filter(payment_date__gte=date_from)
            installments_qs = installments_qs.filter(due_date__gte=date_from)
        if date_to:
            payments_qs = payments_qs.filter(payment_date__lte=date_to)
            installments_qs = installments_qs.filter(due_date__lte=date_to)

        total_expected = (
            installments_qs.aggregate(total=Sum("amount"))["total"] or 0
        )
        total_collected = (
            payments_qs.filter(payment_status="verified").aggregate(
                total=Sum("amount_paid")
            )["total"]
            or 0
        )
        outstanding = max(total_expected - total_collected, 0)
        recovery_rate = round((total_collected / total_expected) * 100, 2) if total_expected else 0

        pending_payments_amount = (
            payments_qs.filter(payment_status="unverified").aggregate(
                total=Sum("amount_paid")
            )["total"]
            or 0
        )

        verified_payments_count = payments_qs.filter(
            payment_status="verified"
        ).count()
        unverified_payments_count = payments_qs.filter(
            payment_status="unverified"
        ).count()
        overdue_installments_count = installments_qs.filter(status="overdue").count()

        monthly_collections = (
            payments_qs.filter(payment_status="verified", payment_date__isnull=False)
            .annotate(period=FinanceDashboardService._get_trunc(period, "payment_date"))
            .values("period")
            .annotate(amount=Sum("amount_paid"))
            .order_by("period")
        )
        monthly_collections = [
            {
                "month": FinanceDashboardService._format_period_label(
                    period, m["period"]
                ),
                "amount": m["amount"] or 0,
            }
            for m in monthly_collections
        ]

        monthly_expected = (
            installments_qs.filter(due_date__isnull=False)
            .annotate(period=FinanceDashboardService._get_trunc(period, "due_date"))
            .values("period")
            .annotate(amount=Sum("amount"))
            .order_by("period")
        )
        monthly_expected = [
            {
                "month": FinanceDashboardService._format_period_label(
                    period, m["period"]
                ),
                "amount": m["amount"] or 0,
            }
            for m in monthly_expected
        ]

        collections_map = {row["month"]: row["amount"] for row in monthly_collections}
        expected_map = {row["month"]: row["amount"] for row in monthly_expected}
        month_keys = sorted(set(collections_map.keys()) | set(expected_map.keys()))

        monthly_summary = []
        monthly_outstanding = []
        monthly_recovery_rate = []
        cumulative_collections = []
        cumulative_expected_total = 0
        cumulative_collected_total = 0

        for month in month_keys:
            expected_amount = expected_map.get(month, 0)
            collected_amount = collections_map.get(month, 0)
            outstanding_amount = max(expected_amount - collected_amount, 0)
            recovery = (
                round((collected_amount / expected_amount) * 100, 2)
                if expected_amount
                else 0
            )

            monthly_summary.append(
                {
                    "month": month,
                    "expected": expected_amount,
                    "collected": collected_amount,
                    "outstanding": outstanding_amount,
                    "recovery_rate": recovery,
                }
            )
            monthly_outstanding.append({"month": month, "amount": outstanding_amount})
            monthly_recovery_rate.append({"month": month, "rate": recovery})

            cumulative_expected_total += expected_amount
            cumulative_collected_total += collected_amount
            cumulative_collections.append(
                {
                    "month": month,
                    "expected": cumulative_expected_total,
                    "collected": cumulative_collected_total,
                    "outstanding": max(
                        cumulative_expected_total - cumulative_collected_total, 0
                    ),
                }
            )

        by_payment_method = (
            payments_qs.filter(payment_status="verified")
            .values("payment_method")
            .annotate(amount=Sum("amount_paid"))
            .order_by("-amount")
        )
        by_payment_method = [
            {"method": row["payment_method"], "amount": row["amount"] or 0}
            for row in by_payment_method
        ]

        faculty_expected = installments_qs.values(
            faculty_id=Coalesce(
                "payment_plan__feessheet__faculty__id",
                "payment_plan__feessheet__department__faculty__id",
                "payment_plan__feessheet__class_fk__department__faculty__id",
            ),
            faculty_name=Coalesce(
                "payment_plan__feessheet__faculty__faculty_name",
                "payment_plan__feessheet__department__faculty__faculty_name",
                "payment_plan__feessheet__class_fk__department__faculty__faculty_name",
            ),
        ).annotate(expected=Sum("amount")).filter(faculty_id__isnull=False)

        faculty_collected = payments_qs.filter(payment_status="verified").values(
            faculty_id=Coalesce(
                "paymentplan__feessheet__faculty__id",
                "paymentplan__feessheet__department__faculty__id",
                "paymentplan__feessheet__class_fk__department__faculty__id",
            ),
            faculty_name=Coalesce(
                "paymentplan__feessheet__faculty__faculty_name",
                "paymentplan__feessheet__department__faculty__faculty_name",
                "paymentplan__feessheet__class_fk__department__faculty__faculty_name",
            ),
        ).annotate(collected=Sum("amount_paid")).filter(faculty_id__isnull=False)

        faculty_map = {}
        for row in faculty_expected:
            faculty_map[str(row["faculty_id"])] = {
                "id": str(row["faculty_id"]),
                "name": row["faculty_name"],
                "expected": row["expected"] or 0,
                "collected": 0,
            }

        for row in faculty_collected:
            key = str(row["faculty_id"])
            if key not in faculty_map:
                faculty_map[key] = {
                    "id": str(row["faculty_id"]),
                    "name": row["faculty_name"],
                    "expected": 0,
                    "collected": 0,
                }
            faculty_map[key]["collected"] = row["collected"] or 0

        by_faculty = []
        for _, row in faculty_map.items():
            expected = row["expected"]
            collected = row["collected"]
            outstanding_faculty = max(expected - collected, 0)
            recovery = round((collected / expected) * 100, 2) if expected else 0
            by_faculty.append(
                {
                    "id": row["id"],
                    "name": row["name"],
                    "expected": expected,
                    "collected": collected,
                    "outstanding": outstanding_faculty,
                    "recovery_rate": recovery,
                }
            )

        by_faculty = sorted(by_faculty, key=lambda x: x["expected"], reverse=True)

        recent_payments_qs = payments_qs.order_by(
            "-payment_date", "-verified_at", "-id"
        )[:10]
        recent_payments = []
        for p in recent_payments_qs:
            student = p.inscription.student if p.inscription else None
            user = student.user if student else None
            if student:
                active_sm = student.get_active_matricule()
                matricule_display = active_sm.matricule if active_sm else None
            else:
                matricule_display = "N/A"
            recent_payments.append(
                {
                    "id": str(p.id),
                    "student_name": f"{user.first_name} {user.last_name}".strip()
                    if user
                    else "N/A",
                    "matricule": matricule_display,
                    "amount": p.amount_paid,
                    "method": p.payment_method,
                    "date": p.payment_date or date.today(),
                    "status": p.payment_status,
                }
            )

        buildings_qs = Building.objects.filter(university=university)
        rooms_qs = Room.objects.filter(building__university=university)
        equipment_qs = Equipment.objects.filter(
            equipmentallocation__room__building__university=university
        ).distinct()

        rooms_by_type = (
            rooms_qs.values("room_type")
            .annotate(count=Count("id"))
            .order_by("-count")
        )
        rooms_by_type = [
            {"type": row["room_type"], "count": row["count"]} for row in rooms_by_type
        ]

        equipment_by_status = (
            equipment_qs.values("status")
            .annotate(count=Count("id"))
            .order_by("-count")
        )
        equipment_by_status = [
            {"status": row["status"], "count": row["count"]}
            for row in equipment_by_status
        ]

        equipment_allocations_active_count = EquipmentAllocation.objects.filter(
            status="active", room__building__university=university
        ).count()

        assets = {
            "buildings_count": buildings_qs.count(),
            "rooms_count": rooms_qs.count(),
            "rooms_available_count": rooms_qs.filter(is_available=True).count(),
            "rooms_by_type": rooms_by_type,
            "equipment_total": equipment_qs.count(),
            "equipment_by_status": equipment_by_status,
            "equipment_under_maintenance_count": equipment_qs.filter(
                status="under_maintenance"
            ).count(),
            "equipment_allocations_active_count": equipment_allocations_active_count,
        }

        return {
            "academic_year": {
                "id": str(academic_year.id),
                "label": academic_year.academic_year,
            },
            "kpis": {
                "total_expected": total_expected,
                "total_collected": total_collected,
                "outstanding": outstanding,
                "recovery_rate": recovery_rate,
                "overdue_installments_count": overdue_installments_count,
                "pending_payments_amount": pending_payments_amount,
                "verified_payments_count": verified_payments_count,
                "unverified_payments_count": unverified_payments_count,
            },
            "trends": {
                "period": period,
                "monthly_collections": monthly_collections,
                "monthly_expected": monthly_expected,
                "monthly_summary": monthly_summary,
                "monthly_outstanding": monthly_outstanding,
                "monthly_recovery_rate": monthly_recovery_rate,
                "cumulative_collections": cumulative_collections,
            },
            "breakdowns": {
                "by_faculty": by_faculty,
                "by_payment_method": by_payment_method,
            },
            "recent_payments": recent_payments,
            "assets": assets,
        }
