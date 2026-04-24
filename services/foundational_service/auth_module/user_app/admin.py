# Register your models here.
from django.contrib import admin
from django.db import transaction
from import_export import fields, resources
from import_export.admin import ImportExportModelAdmin
from import_export.widgets import ForeignKeyWidget, ManyToManyWidget
from unfold.admin import ModelAdmin

from services.foundational_service.geo_module.colline_app.models import Colline
from services.foundational_service.geo_module.country_app.models import Country
from services.foundational_service.auth_module.authentication_app.services import UserService

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

    def save_model(self, request, obj, form, change):
        if not change:
            super().save_model(request, obj, form, change)
            return

        old = User.objects.get(pk=obj.pk)
        service = UserService()

        with transaction.atomic():
            # Sync EmailDevice when requires_2fa_email changes
            if old.requires_2fa_email != obj.requires_2fa_email:
                if obj.requires_2fa_email:
                    service.setup_email_2fa(obj)
                else:
                    from django_otp.plugins.otp_email.models import EmailDevice
                    EmailDevice.objects.filter(user=obj).delete()

            # Sync TOTPDevice when requires_2fa_qr changes
            if old.requires_2fa_qr != obj.requires_2fa_qr:
                if obj.requires_2fa_qr:
                    service.setup_totp_2fa(obj)
                else:
                    from django_otp.plugins.otp_totp.models import TOTPDevice
                    TOTPDevice.objects.filter(user=obj).delete()
                    obj.totp_secret_key = None

            # Sync StaticDevice when requires_2fa_static changes
            if old.requires_2fa_static != obj.requires_2fa_static:
                if obj.requires_2fa_static:
                    service.setup_static_2fa(obj)
                else:
                    from django_otp.plugins.otp_static.models import StaticDevice
                    StaticDevice.objects.filter(user=obj).delete()

            # If master 2FA disabled, clean everything
            if old.requires_2fa and not obj.requires_2fa:
                from django_otp.plugins.otp_email.models import EmailDevice
                from django_otp.plugins.otp_totp.models import TOTPDevice
                from django_otp.plugins.otp_static.models import StaticDevice
                EmailDevice.objects.filter(user=obj).delete()
                TOTPDevice.objects.filter(user=obj).delete()
                StaticDevice.objects.filter(user=obj).delete()
                obj.requires_2fa_email = False
                obj.requires_2fa_qr = False
                obj.requires_2fa_static = False
                obj.totp_secret_key = None

            # Ensure requires_2fa is consistent with sub-flags
            obj.requires_2fa = obj.requires_2fa_email or obj.requires_2fa_qr or obj.requires_2fa_static

            # Ensure spoken_languages is never None (MySQL JSONField strict mode)
            if obj.spoken_languages is None:
                obj.spoken_languages = []

            super().save_model(request, obj, form, change)
