# Register your models here.
from django.contrib import admin
from django.db import models
from import_export import fields, resources
from import_export.admin import ImportExportModelAdmin
from import_export.widgets import ForeignKeyWidget, ManyToManyWidget
from unfold.admin import ModelAdmin

from services.core_service.academic_module.department_app.models import Department
from services.core_service.academic_module.university_app.models import UniversityDegree
from services.core_service.student_module.highschool_info_app.models import (
    Certificate,
    Highschool,
    TrainingCenter,
)
from services.core_service.student_module.parent_app.models import Parent
from services.foundational_service.auth_module.user_app.models import User
from services.foundational_service.geo_module.colline_app.models import Colline

from .models import Student, StudentFile, StudentGraduateInfo, StudentHsInfo, StudentMatricule, Training

# ----------------------------
# StudentMatricule Inline
# ----------------------------
class StudentMatriculeInline(admin.TabularInline):
    model = StudentMatricule
    extra = 0
    readonly_fields = ("matricule", "type_formation", "academic_year")
    fields = ("type_formation", "matricule", "academic_year")
    can_delete = False
    show_change_link = True
    verbose_name = "Matricule par TypeFormation"
    verbose_name_plural = "Matricules (par TypeFormation)"


# ----------------------------
# StudentMatricule Resource
# ----------------------------
class StudentMatriculeResource(resources.ModelResource):
    student_email = fields.Field(
        column_name="student_email",
        attribute="student",
        widget=ForeignKeyWidget(User, "email"),
    )
    student_matricule_legacy = fields.Field(
        column_name="student_matricule_legacy",
        attribute="student",
        widget=ForeignKeyWidget(Student, "matricule"),
    )
    type_formation_code = fields.Field(
        column_name="type_formation_code",
        attribute="type_formation",
        widget=ForeignKeyWidget(
            "faculty_app.TypeFormation", "code"
        ),
    )
    academic_year_label = fields.Field(
        column_name="academic_year",
        attribute="academic_year",
        widget=ForeignKeyWidget(
            "university_app.AcademicYear", "academic_year"
        ),
    )

    class Meta:
        model = StudentMatricule
        fields = (
            "id",
            "student",
            "student_email",
            "student_matricule_legacy",
            "type_formation",
            "type_formation_code",
            "matricule",
            "academic_year",
            "academic_year_label",
        )
        export_order = (
            "id",
            "student_email",
            "student_matricule_legacy",
            "type_formation_code",
            "matricule",
            "academic_year_label",
        )


@admin.register(StudentMatricule)
class StudentMatriculeAdmin(ImportExportModelAdmin, ModelAdmin):
    resource_class = StudentMatriculeResource
    list_display = (
        "matricule",
        "student",
        "type_formation",
        "academic_year",
    )
    search_fields = (
        "matricule",
        "student__user__email",
        "student__user__first_name",
        "student__user__last_name",
        "type_formation__code",
        "type_formation__name",
    )
    list_filter = (
        "type_formation",
        "academic_year",
    )
    ordering = ("type_formation", "matricule")
    readonly_fields = ("matricule", "student", "type_formation", "academic_year")

    fieldsets = (
        (
            "Matricule Information",
            {
                "fields": (
                    "student",
                    "type_formation",
                    "matricule",
                    "academic_year",
                )
            },
        ),
    )


# ----------------------------
# Student Resource
# ----------------------------
class StudentResource(resources.ModelResource):
    colline_name = fields.Field(
        column_name="colline_name",
        attribute="colline",
        widget=ForeignKeyWidget(Colline, "colline_name"),
    )
    user_email = fields.Field(
        column_name="user_email",
        attribute="user",
        widget=ForeignKeyWidget(User, "email"),
    )
    parent_ids = fields.Field(
        column_name="parents",
        attribute="parent",
        widget=ManyToManyWidget(Parent, field="id", separator=","),
    )
    matricule = fields.Field(
        column_name="matricule",
        attribute="id",  # dummy, will be overwritten by dehydrate
    )

    class Meta:
        model = Student
        fields = (
            "id",
            "matricule",
            "user",
            "user_email",
            "colline",
            "colline_name",
            "cam",
            "parent",
            "parent_ids",
        )
        export_order = (
            "id",
            "matricule",
            "user_email",
            "colline_name",
            "cam",
            "parent_ids",
        )

    def dehydrate_matricule(self, student):
        """Calcule le matricule à exporter (le plus récent)."""
        active_sm = student.get_active_matricule()
        return active_sm.matricule if active_sm else ""


# ----------------------------
# Student Admin
# ----------------------------
@admin.register(Student)
class StudentAdmin(ImportExportModelAdmin, ModelAdmin):
    resource_class = StudentResource
    list_display = ("get_primary_matricule", "user", "colline", "cam", "get_all_matricules")
    search_fields = ("matricules__matricule", "user__email", "colline__colline_name")
    list_filter = ("colline",)
    ordering = ("id",)
    inlines = [StudentMatriculeInline]

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        # Précharger les matricules et leurs types pour éviter N+1
        return qs.prefetch_related('matricules__type_formation')

    def get_primary_matricule(self, obj):
        """Affiche le matricule principal (le plus récent) de l'étudiant."""
        active_sm = obj.get_active_matricule()
        return active_sm.matricule if active_sm else "-"
    get_primary_matricule.short_description = "Matricule"

    def get_all_matricules(self, obj):
        """Affiche tous les matricules de l'étudiant (par TypeFormation)."""
        # obj.matricules est déjà préchargé
        matricules = obj.matricules.all()
        if not matricules:
            return "-"
        return ", ".join([f"{sm.type_formation.code}: {sm.matricule}" for sm in matricules])
    get_all_matricules.short_description = "Matricules (par type)"

    formfield_overrides = {
        models.CharField: {
            "widget": admin.widgets.AdminTextInputWidget(attrs={"class": "vTextField"})
        },
    }


# ----------------------------
# Training Resource
# ----------------------------
class TrainingResource(resources.ModelResource):
    training_center_name = fields.Field(
        column_name="training_center",
        attribute="training_center",
        widget=ForeignKeyWidget(TrainingCenter, "name"),
    )

    class Meta:
        model = Training
        fields = (
            "id",
            "domaine",
            "certificate",
            "training_center",
            "training_center_name",
        )
        export_order = ("id", "domaine", "certificate", "training_center_name")


@admin.register(Training)
class TrainingAdmin(ImportExportModelAdmin, ModelAdmin):
    resource_class = TrainingResource
    list_display = ("domaine", "certificate", "training_center")
    search_fields = ("domaine", "certificate", "training_center__name")
    ordering = ("domaine",)


# ----------------------------
# StudentHsInfo Resource
# ----------------------------
class StudentHsInfoResource(resources.ModelResource):
    student_matricule = fields.Field(
        column_name="student_matricule",
        attribute="student",
        widget=ForeignKeyWidget(Student, "matricule"),
    )
    highschool_name = fields.Field(
        column_name="highschool",
        attribute="highschool",
        widget=ForeignKeyWidget(Highschool, "name"),
    )
    certificate_name = fields.Field(
        column_name="certificate",
        attribute="certificate",
        widget=ForeignKeyWidget(Certificate, "name"),
    )
    formation_ids = fields.Field(
        column_name="formations",
        attribute="formation",
        widget=ManyToManyWidget(Training, field="id", separator=","),
    )

    class Meta:
        model = StudentHsInfo
        fields = (
            "id",
            "student",
            "student_matricule",
            "highschool",
            "highschool_name",
            "certificate",
            "certificate_name",
            "se_mark",
            "date_of_obtention",
            "formation",
            "formation_ids",
        )
        export_order = (
            "id",
            "student_matricule",
            "highschool_name",
            "certificate_name",
            "se_mark",
            "date_of_obtention",
            "formation_ids",
        )


@admin.register(StudentHsInfo)
class StudentHsInfoAdmin(ImportExportModelAdmin, ModelAdmin):
    resource_class = StudentHsInfoResource
    list_display = (
        "student",
        "highschool",
        "certificate",
        "se_mark",
        "date_of_obtention",
    )
    search_fields = (
        "student__matricules__matricule",  # Cherche dans StudentMatricule
        "highschool__name",
        "certificate__name",
    )
    ordering = ("date_of_obtention",)


# ----------------------------
# StudentGraduateInfo Resource
# ----------------------------
class StudentGraduateInfoResource(resources.ModelResource):
    student_matricule = fields.Field(
        column_name="student_matricule",
        attribute="student",
        widget=ForeignKeyWidget(Student, "matricule"),
    )
    department_name = fields.Field(
        column_name="department",
        attribute="department",
        widget=ForeignKeyWidget(Department, "department_name"),
    )
    degree_name = fields.Field(
        column_name="degree",
        attribute="degree",
        widget=ForeignKeyWidget(UniversityDegree, "degree_name"),
    )

    class Meta:
        model = StudentGraduateInfo
        fields = (
            "id",
            "student",
            "student_matricule",
            "department",
            "department_name",
            "option",
            "mention",
            "degree",
            "degree_name",
        )
        export_order = (
            "id",
            "student_matricule",
            "department_name",
            "option",
            "mention",
            "degree_name",
        )


@admin.register(StudentGraduateInfo)
class StudentGraduateInfoAdmin(ImportExportModelAdmin, ModelAdmin):
    resource_class = StudentGraduateInfoResource
    list_display = ("student", "department", "option", "mention", "degree")
    search_fields = (
        "student__matricules__matricule",  # Cherche dans StudentMatricule
        "department__department_name",
        "degree__degree_name",
    )
    ordering = ("student",)


@admin.register(StudentFile)
class StudentFileAdmin(ModelAdmin):
    list_display = ("student", "file_type", "file_name", "is_verified", "uploaded_at")
    search_fields = (
        "student__matricules__matricule",  # Cherche dans StudentMatricule
        "file_name",
    )
    list_filter = ("file_type", "is_verified")
    ordering = ("-uploaded_at",)
