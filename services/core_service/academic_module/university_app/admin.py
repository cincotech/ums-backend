# Register your models here.
from django.contrib import admin
from django.db import models
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
    list_display = ("academic_year", "civil_year", "start_date", "end_date")
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
