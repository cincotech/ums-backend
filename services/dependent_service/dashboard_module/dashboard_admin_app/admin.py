from django.contrib import admin

from .models import (
    UniversityConfiguration,
    UniversityNotification,
    UniversityStatistics,
)


@admin.register(UniversityConfiguration)
class UniversityConfigurationAdmin(admin.ModelAdmin):
    list_display = ("university", "category", "key", "is_active", "created_at")
    list_filter = ("university", "category", "is_active", "created_at")
    search_fields = ("key", "university__university_name")
    readonly_fields = ("id", "created_at", "updated_at")

    fieldsets = (
        (
            "Configuration",
            {"fields": ("university", "category", "key", "value", "description")},
        ),
        ("Status", {"fields": ("is_active",)}),
        (
            "Audit",
            {
                "fields": ("created_by", "modified_by", "created_at", "updated_at"),
                "classes": ("collapse",),
            },
        ),
    )


@admin.register(UniversityStatistics)
class UniversityStatisticsAdmin(admin.ModelAdmin):
    list_display = (
        "university",
        "total_students",
        "total_teachers",
        "total_courses",
        "calculated_at",
    )
    list_filter = ("university", "calculated_at")
    search_fields = ("university__university_name",)
    readonly_fields = ("id", "calculated_at")

    fieldsets = (
        ("University", {"fields": ("university",)}),
        (
            "Academic",
            {
                "fields": (
                    "total_students",
                    "total_teachers",
                    "total_faculties",
                    "total_departments",
                    "total_courses",
                )
            },
        ),
        (
            "Operations",
            {
                "fields": (
                    "active_enrollments",
                    "completed_exams",
                    "pending_document_requests",
                    "pending_payments",
                )
            },
        ),
        (
            "Data",
            {"fields": ("statistics_data", "calculated_at"), "classes": ("collapse",)},
        ),
    )


@admin.register(UniversityNotification)
class UniversityNotificationAdmin(admin.ModelAdmin):
    list_display = (
        "title",
        "recipient",
        "notification_type",
        "priority",
        "is_read",
        "created_at",
    )
    list_filter = ("notification_type", "priority", "is_read", "created_at")
    search_fields = ("title", "recipient__email", "university__university_name")
    readonly_fields = ("id", "created_at", "read_at")

    fieldsets = (
        (
            "Notification",
            {"fields": ("university", "recipient", "title", "message", "action_url")},
        ),
        ("Type & Priority", {"fields": ("notification_type", "priority")}),
        ("Status", {"fields": ("is_read", "read_at", "created_at")}),
    )
