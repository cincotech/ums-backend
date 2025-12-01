from django.db.models import Avg, Count

from .models import (
    AcademicPerformanceReport,
    CourseSatisfactionSurvey,
    ProgramExecutionTracking,
    StudentRetentionAudit,
)


class QualityDirectorService:
    @staticmethod
    def get_academic_performance_summary():
        return AcademicPerformanceReport.objects.aggregate(
            avg_success=Avg("success_rate"),
            avg_failure=Avg("failure_rate"),
            avg_grade=Avg("average_grade"),
        )

    @staticmethod
    def get_program_execution_status():
        programs = ProgramExecutionTracking.objects.all()
        return [
            {
                "program_name": p.program_name,
                "academic_year": p.academic_year,
                "progress": p.progress_percentage,
                "objectives_met": p.objectives_met,
            }
            for p in programs
        ]

    @staticmethod
    def get_student_retention_summary():
        audits = StudentRetentionAudit.objects.all().order_by("-academic_year")
        return [
            {
                "academic_year": a.academic_year,
                "retention_rate": a.retention_rate,
                "dropout_rate": a.dropout_rate,
                "dropout_reasons": a.dropout_reasons,
            }
            for a in audits
        ]

    @staticmethod
    def get_course_satisfaction_stats():
        return CourseSatisfactionSurvey.objects.aggregate(
            avg_course_quality=Avg("course_quality_rating"),
            avg_teacher_quality=Avg("teacher_rating"),
            avg_learning_env=Avg("environment_rating"),
        )
