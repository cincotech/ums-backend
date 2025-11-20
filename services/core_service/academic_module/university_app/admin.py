# Register your models here.
from django.contrib import admin, messages
from django.db import models, transaction
from django.utils.html import format_html
from import_export import fields, resources
from import_export.admin import ImportExportModelAdmin
from import_export.widgets import ForeignKeyWidget
from unfold.admin import ModelAdmin

from services.foundational_service.geo_module.country_app.models import Country

from .models import AcademicYear, University, UniversityDegree


# ----------------------------
# AcademicYear Resource
# ----------------------------
class AcademicYearResource(resources.ModelResource):
    class Meta:
        model = AcademicYear
        fields = (
            "id",
            "academic_year",
            "description",
            "civil_year",
            "start_date",
            "end_date",
        )
        export_order = (
            "id",
            "academic_year",
            "civil_year",
            "start_date",
            "end_date",
            "description",
        )


# ----------------------------
# University Resource
# ----------------------------
class UniversityResource(resources.ModelResource):
    country_name = fields.Field(
        column_name="country_name",
        attribute="country",
        widget=ForeignKeyWidget(Country, "country_name"),
    )

    class Meta:
        model = University
        fields = (
            "id",
            "university_name",
            "university_abrev",
            "country",
            "country_name",
        )
        export_order = ("id", "university_name", "university_abrev", "country_name")


# ----------------------------
# UniversityDegree Resource
# ----------------------------
class UniversityDegreeResource(resources.ModelResource):
    class Meta:
        model = UniversityDegree
        fields = ("id", "degree_name", "description")
        export_order = ("id", "degree_name", "description")


# ----------------------------
# AcademicYear Admin
# ----------------------------
@admin.register(AcademicYear)
class AcademicYearAdmin(ImportExportModelAdmin, ModelAdmin):
    resource_class = AcademicYearResource
    list_display = (
        "academic_year",
        "civil_year",
        "start_date",
        "end_date",
        "is_closed",
        "close_year_button",
    )
    search_fields = ("academic_year", "civil_year")
    ordering = ("-start_date",)

    fieldsets = (
        (
            "Academic Year Information",
            {
                "fields": (
                    "academic_year",
                    "description",
                    "civil_year",
                    "start_date",
                    "end_date",
                )
            },
        ),
    )

    formfield_overrides = {
        models.CharField: {
            "widget": admin.widgets.AdminTextInputWidget(attrs={"class": "vTextField"})
        },
    }

    # --------------- Custom Action ----------------
    actions = ["close_academic_years"]

    def close_academic_years(self, request, queryset):
        """
        Admin action to close selected academic years
        """
        for year in queryset:
            if year.is_closed:
                self.message_user(
                    request, f"{year} is already closed.", level=messages.WARNING
                )
                continue
            # Close the year; use request.user as closed_by
            with transaction.atomic():
                year.close_year(closed_by_user=request.user)
            self.message_user(
                request, f"{year} closed successfully.", level=messages.SUCCESS
            )

    close_academic_years.short_description = "Close selected Academic Years"

    # Optional: add a button in list_display
    def close_year_button(self, obj):
        if not obj.is_closed:
            return format_html(
                '<a class="button" href="{}">Close Year</a>', f"./{obj.id}/close/"
            )
        return "Closed"

    close_year_button.short_description = "Close Year"
    close_year_button.allow_tags = True


# ----------------------------
# University Admin
# ----------------------------
@admin.register(University)
class UniversityAdmin(ImportExportModelAdmin, ModelAdmin):
    resource_class = UniversityResource
    list_display = ("university_name", "university_abrev", "country")
    list_filter = ("country",)
    search_fields = ("university_name", "university_abrev", "country__country_name")
    ordering = ("university_name",)

    fieldsets = (
        (
            "University Information",
            {"fields": ("university_name", "university_abrev", "country")},
        ),
    )

    formfield_overrides = {
        models.CharField: {
            "widget": admin.widgets.AdminTextInputWidget(attrs={"class": "vTextField"})
        },
    }


# ----------------------------
# UniversityDegree Admin
# ----------------------------
@admin.register(UniversityDegree)
class UniversityDegreeAdmin(ImportExportModelAdmin, ModelAdmin):
    resource_class = UniversityDegreeResource
    list_display = ("degree_name", "description")
    search_fields = ("degree_name",)
    ordering = ("degree_name",)

    fieldsets = (
        ("University Degree Information", {"fields": ("degree_name", "description")}),
    )

    formfield_overrides = {
        models.CharField: {
            "widget": admin.widgets.AdminTextInputWidget(attrs={"class": "vTextField"})
        },
    }
