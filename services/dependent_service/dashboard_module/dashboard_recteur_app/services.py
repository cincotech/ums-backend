from django.db.models import Avg, Count

class RectorAnalyticsService:
    @staticmethod
    def payment_overview():
        return {
            "total_students": 1280,
            "students_fully_paid": 980,
            "students_with_debt": 300,
            "recovery_rate": round((980 / 1280) * 100, 2),
        }

    @staticmethod
    def academic_performance():
        return {
            "success_rate": 78.4,
            "retention_rate": 84.2,
            "program_advancement": 72.1,
        }
