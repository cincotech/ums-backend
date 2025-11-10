# Register your models here.
from django.contrib import admin
from unfold.admin import ModelAdmin  # modern UI admin

from .models import Profile, Supervisor
from .resources import ProfileResource


@admin.register(Profile)
class ProfileAdmin(ModelAdmin):
    resource_class = ProfileResource
    list_display = ("user", "position", "start_date", "end_date")
    list_filter = ("position", "start_date")
    search_fields = ("user__email", "user__username", "position")
    autocomplete_fields = ("user", "room", "faculty", "university")
    ordering = ("user",)
    fieldsets = (
        ("User Information", {"fields": ("user", "position")}),
        ("Assignment Details", {"fields": ("room", "faculty", "university")}),
        ("Dates", {"fields": ("start_date", "end_date")}),
    )


@admin.register(Supervisor)
class SupervisorAdmin(ModelAdmin):
    list_display = ("user", "is_supervisor_active")
    list_filter = ("is_supervisor_active",)
    search_fields = ("user__email", "user__username")
    autocomplete_fields = ("user",)
    ordering = ("user",)
