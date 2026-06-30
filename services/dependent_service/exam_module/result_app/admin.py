from django.contrib import admin
from unfold.admin import ModelAdmin

from .models import CompiledResult, Result, Session, Supplement


@admin.register(Session)
class SessionAdmin(ModelAdmin):
    list_display = ["session_name"]
    search_fields = ["session_name"]


@admin.register(Result)
class ResultAdmin(ModelAdmin):
    list_display = ["course", "inscription", "session", "mark"]
    list_filter = ["session", "course"]
    search_fields = ["inscription__student__matricules__matricule"]


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
