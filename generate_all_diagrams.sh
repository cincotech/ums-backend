#!/bin/bash

set -e

echo "🎨 UMS Diagram Generation"
echo "========================"

mkdir -p docs/diagrams/plantuml docs/diagrams/png docs/diagrams/svg

# Activate virtual environment if it exists
if [ -d "venv/bin" ]; then
    source venv/bin/activate
fi

echo "🔧 Generating PlantUML diagrams..."
python manage.py generate_diagrams --type=all

echo "📊 Exporting models info..."
python manage.py export_models_info

echo "📊 Django-extensions graphs..."
python manage.py graph_models -a -g -o docs/diagrams/complete_models.png
python manage.py graph_models country_app province_app commune_app zone_app colline_app authorization_app user_app authentication_app guest_app -g -o docs/diagrams/foundational_service.png
python manage.py graph_models class_app course_app department_app faculty_app module_app teacher_app university_app quality_app public_app -g -o docs/diagrams/academic_module.png
python manage.py graph_models card_app highschool_info_app inscription_app parent_app student_profile_app -g -o docs/diagrams/student_module.png
python manage.py graph_models document_app request_app -g -o docs/diagrams/document_module.png
python manage.py graph_models attendance_app exam_app result_app -g -o docs/diagrams/exam_module.png
python manage.py graph_models building_app equipment_app room_app -g -o docs/diagrams/infrastructure_module.png
python manage.py graph_models scheduling_app -g -o docs/diagrams/scheduling_module.png

if command -v plantuml &> /dev/null; then
    echo "🖼️ Converting PlantUML to PNG/SVG..."
    plantuml -tpng docs/diagrams/plantuml/*.puml -o ../png/
    plantuml -tsvg docs/diagrams/plantuml/*.puml -o ../svg/
else
    echo "⚠️  PlantUML not installed. Install: sudo apt-get install plantuml"
fi

echo "✅ Complete! Files in docs/diagrams/"
