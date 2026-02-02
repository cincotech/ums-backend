#!/usr/bin/env bash
set -e

echo "📊 Generating Django model diagrams (.dot + .png by group)"

# Activate virtualenv
source venv/bin/activate

# Django settings
export DJANGO_SETTINGS_MODULE="ums_backend.settings"  # <-- adjust

# Directories
DOCS_DIR="docs"
DOT_DIR="$DOCS_DIR/dot"
IMG_DIR="$DOCS_DIR/images"
mkdir -p "$DOT_DIR" "$IMG_DIR"

# ------------------------
# Define app groups
# ------------------------
declare -A APP_GROUPS

APP_GROUPS[location]=(
country_app province_app commune_app zone_app colline_app
)

APP_GROUPS[users]=(
authorization_app user_app authentication_app parent_app student_profile_app
)

APP_GROUPS[academic]=(
class_app course_app department_app faculty_app module_app teacher_app university_app highschool_info_app inscription_app student_profile_app document_app request_app attendance_app exam_app result_app
)

APP_GROUPS[dashboard]=(
dashboard_super_admin_app dashboard_recteur_app dashboard_quality_director_app dashboard_student_services_app dashboard_collection_agent_app dashboard_student_app dashboard_academic_secretary_app dashboard_alumni_app dashboard_admin_app dashboard_doyen_app dashboard_academic_app dashboard_shared_app
)

APP_GROUPS[core]=(
quality_app card_app building_app equipment_app room_app event_notification_app scheduling_app core token_blacklist
)

# APP_GROUPS[django]=(
# unfold unfold_filters unfold_forms unfold_inlines unfold_importexport unfold_guardian unfold_simple_history unfold_location_field unfold_constance admin auth contenttypes sessions messages staticfiles django_otp otp_static otp_totp otp_email django_extensions rest_framework corsheaders import_export simple_history drf_spectacular drf_spectacular_sidecar django_filters
# )

# ------------------------
# Function to generate diagram for a group
# ------------------------
generate_group_diagram() {
    local group_name=$1
    shift
    local apps=("$@")

    DOT_FILE="$DOT_DIR/${group_name}.dot"
    PNG_FILE="$IMG_DIR/${group_name}.png"

    echo "➡️ Generating group diagram for [$group_name] with apps: ${apps[*]}"

    # Generate .dot for all apps in this group
    python manage.py graph_models "${apps[@]}" --dot -o "$DOT_FILE"

    # Convert to PNG
    dot -Tpng "$DOT_FILE" -o "$PNG_FILE"

    echo "✅ Diagram generated: $PNG_FILE"
}

# ------------------------
# Loop through each group
# ------------------------
for group in "${!APP_GROUPS[@]}"; do
    generate_group_diagram "$group" "${APP_GROUPS[$group][@]}"
done

echo "🎉 All group diagrams generated in $IMG_DIR"
