from django.contrib import admin
from import_export.admin import ImportExportModelAdmin
from unfold.admin import ModelAdmin
from unfold.contrib.import_export.forms import ImportForm, SelectableFieldsExportForm

from .models import Country

# ===============================


# ===============================
# ADMIN CLASS WITH REPORT ACTIONS
# ===============================
@admin.register(Country)
class CountryAdmin(ModelAdmin, ImportExportModelAdmin):
    import_form_class = ImportForm
    export_form_class = SelectableFieldsExportForm

    list_display = ("country_name", "code", "id")
    search_fields = ("country_name", "code")
    list_filter = ("code",)

    # Unfold style (if you're using Unfold Admin)
    unfold_icon = "globe"  # nice icon for Unfold
    unfold_title = "Country Manager"
