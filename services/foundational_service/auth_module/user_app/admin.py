# Register your models here.
from django.contrib import admin
from import_export import fields, resources
from import_export.admin import ImportExportModelAdmin
from import_export.widgets import ForeignKeyWidget, ManyToManyWidget
from unfold.admin import ModelAdmin

from services.foundational_service.geo_module.colline_app.models import Colline
from services.foundational_service.geo_module.country_app.models import Country

from .models import Role, User


# ----------------------------
# Role Admin
# ----------------------------
@admin.register(Role)
class RoleAdmin(ModelAdmin, ImportExportModelAdmin):
    list_display = ("name", "description")
    search_fields = ("name",)
    ordering = ("name",)
    fieldsets = (("Role Information", {"fields": ("name", "description")}),)


# ----------------------------
# User Resource for Import/Export
# ----------------------------
class UserResource(resources.ModelResource):
    country_name = fields.Field(
        column_name="country_name",
        attribute="nationality",
        widget=ForeignKeyWidget(Country, "country_name"),
    )
    residence_names = fields.Field(
        column_name="residence_names",
        attribute="residence",
        widget=ManyToManyWidget(Colline, field="colline_name", separator=","),
    )
    role_name = fields.Field(
        column_name="role_name",
        attribute="role",
        widget=ForeignKeyWidget(Role, "name"),
    )

    class Meta:
        model = User
        fields = (
            "id",
            "email",
            "phone_number",
            "gender",
            "birth_date",
            "country_name",
            "residence_names",
            "marital_status",
            "role_name",
            "email_verified",
            "requires_2fa",
        )
        export_order = fields


# ----------------------------
# User Admin (Unfold + Import/Export)
# ----------------------------
@admin.register(User)
class UserAdmin(ImportExportModelAdmin, ModelAdmin):
    resource_class = UserResource
    list_display = (
        "email",
        "phone_number",
        "gender",
        "nationality",
        "role",
        "email_verified",
        "requires_2fa",
        "university",
    )
    list_filter = ("gender", "marital_status", "email_verified", "requires_2fa")
    search_fields = ("email", "phone_number", "role__name")
    ordering = ("email",)

    fieldsets = (
        (
            "Personal Info",
            {"fields": ("email", "phone_number", "gender", "birth_date", "university")},
        ),
        (
            "Location & Nationality",
            {"fields": ("nationality", "residence", "marital_status")},
        ),
        ("Role & Access", {"fields": ("role", "email_verified")}),
        (
            "2FA Settings",
            {
                "fields": (
                    "requires_2fa",
                    "requires_2fa_qr",
                    "requires_2fa_email",
                    "requires_2fa_static",
                )
            },
        ),
        ("Other", {"fields": ("spoken_languages", "profile_picture")}),
    )

    filter_horizontal = ("residence",)
