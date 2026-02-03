import time

from django.conf import settings
from django.core.cache import cache
from django.core.mail import send_mail
from django.db import connection


class HealthCheckService:
    """Service to check system health"""

    @staticmethod
    def send_error_notification(error_type, error_message):
        """Send email notification when error occurs"""
        try:
            subject = f"UMS System Health Alert: {error_type}"
            message = f"""System Health Check Failed

Error Type: {error_type}
Error Message: {error_message}
Timestamp: {time.strftime('%Y-%m-%d %H:%M:%S')}

Please check the system immediately."""
            send_mail(
                subject,
                message,
                settings.DEFAULT_FROM_EMAIL,
                [settings.ADMIN_EMAIL],
                fail_silently=True,
            )
        except Exception as e:
            print(f"Failed to send error notification: {str(e)}")

    @staticmethod
    def check_database():
        """Check database connectivity"""
        try:
            with connection.cursor() as cursor:
                cursor.execute("SELECT 1")
            return {"status": "healthy", "message": "Database connection successful"}
        except Exception as e:
            error_msg = f"Database error: {str(e)}"
            HealthCheckService.send_error_notification("Database", error_msg)
            return {"status": "unhealthy", "message": error_msg}

    @staticmethod
    def check_cache():
        """Check cache connectivity"""
        try:
            test_key = "health_check_test"
            test_value = "test"
            cache.set(test_key, test_value, 10)
            result = cache.get(test_key)
            cache.delete(test_key)

            if result == test_value:
                return {"status": "healthy", "message": "Cache working properly"}
            error_msg = "Cache read/write failed"
            HealthCheckService.send_error_notification("Cache", error_msg)
            return {"status": "unhealthy", "message": error_msg}
        except Exception as e:
            error_msg = f"Cache error: {str(e)}"
            HealthCheckService.send_error_notification("Cache", error_msg)
            return {"status": "unhealthy", "message": error_msg}

    @staticmethod
    def get_system_info():
        """Get basic system information"""
        return {
            "debug_mode": settings.DEBUG,
            "allowed_hosts": settings.ALLOWED_HOSTS,
            "database_engine": settings.DATABASES["default"]["ENGINE"],
        }

    @staticmethod
    def perform_health_check():
        """Perform complete health check"""
        start_time = time.time()

        db_status = HealthCheckService.check_database()
        cache_status = HealthCheckService.check_cache()
        system_info = HealthCheckService.get_system_info()

        overall_status = (
            "healthy"
            if (
                db_status["status"] == "healthy" and cache_status["status"] == "healthy"
            )
            else "unhealthy"
        )

        response_time = round((time.time() - start_time) * 1000, 2)

        return {
            "status": overall_status,
            "timestamp": time.time(),
            "response_time_ms": response_time,
            "checks": {
                "database": db_status,
                "cache": cache_status,
            },
            "system": system_info,
        }
