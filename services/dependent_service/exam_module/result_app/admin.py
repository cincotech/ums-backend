from django.contrib import admin
from unfold.admin import ModelAdmin

from .models import CompiledResult, GradeChangeHistory, Result, Session, Supplement


@admin.register(Session)
class SessionAdmin(ModelAdmin):
    list_display = ["session_name"]
    search_fields = ["session_name"]


@admin.register(Result)
class ResultAdmin(ModelAdmin):
    list_display = ["course", "inscription", "session", "mark"]
    list_filter = ["session", "course"]
    search_fields = ["inscription__student__matricules__matricule"]


@admin.register(GradeChangeHistory)
class GradeChangeHistoryAdmin(ModelAdmin):
    list_display = ["result", "previous_mark", "new_mark", "changed_by", "created_at"]
    list_filter = ["created_at"]
    search_fields = [
        "result__inscription__student__matricules__matricule",
        "result__course__course_name",
        "changed_by__first_name",
        "changed_by__last_name",
    ]


@admin.register(CompiledResult)
class CompiledResultAdmin(ModelAdmin):
    list_display = ["inscription", "average_mark", "status", "is_promoted"]
    list_filter = ["status", "is_promoted"]
    search_fields = ["inscription__student__matricules__matricule"]


@admin.register(Supplement)
class SupplementAdmin(ModelAdmin):
    list_display = ["inscription", "course", "mark", "validation", "validation_date"]
    list_filter = ["validation", "course"]
    search_fields = ["inscription__student__matricules__matricule"]
