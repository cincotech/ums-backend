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

from .models import Student, StudentFile, StudentGraduateInfo, StudentHsInfo, Training


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


# ----------------------------
# Student Admin
# ----------------------------
@admin.register(Student)
class StudentAdmin(ImportExportModelAdmin, ModelAdmin):
    resource_class = StudentResource
    list_display = ("matricule", "user", "colline", "cam")
    search_fields = ("matricule", "user__email", "colline__colline_name")
    list_filter = ("colline",)
    ordering = ("matricule",)

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
    search_fields = ("student__matricule", "highschool__name", "certificate__name")
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
        "student__matricule",
        "department__department_name",
        "degree__degree_name",
    )
    ordering = ("student",)


@admin.register(StudentFile)
class StudentFileAdmin(ModelAdmin):
    list_display = ("student", "file_type", "file_name", "is_verified", "uploaded_at")
    search_fields = ("student__matricule", "file_name")
    list_filter = ("file_type", "is_verified")
    ordering = ("-uploaded_at",)
