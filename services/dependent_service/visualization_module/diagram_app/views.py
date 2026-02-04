from pathlib import Path

from django.apps import apps
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from .plantuml_generator import PlantUMLGenerator


class DiagramListView(APIView):
    """List all available diagram files"""

    def get(self, request):
        diagrams_dir = Path("docs/diagrams")

        if not diagrams_dir.exists():
            return Response(
                {
                    "message": "No diagrams generated yet. Run ./generate_all_diagrams.sh"
                },
                status=status.HTTP_404_NOT_FOUND,
            )

        diagrams = []
        for file in diagrams_dir.rglob("*"):
            if file.is_file() and file.suffix in [".puml", ".png", ".svg", ".dot"]:
                diagrams.append(
                    {
                        "name": file.name,
                        "path": str(file.relative_to(diagrams_dir.parent)),
                        "type": file.suffix[1:],
                        "size": file.stat().st_size,
                    }
                )

        return Response({"count": len(diagrams), "diagrams": diagrams})


class GenerateDiagramView(APIView):
    """Generate diagrams on-demand via API"""

    def post(self, request):
        diagram_type = request.data.get("diagram_type", "all")
        module_filter = request.data.get("module")
        scenario = request.data.get("scenario")

        generator = PlantUMLGenerator()

        try:
            if diagram_type == "all":
                files = generator.generate_all(module_filter)
            elif diagram_type == "class":
                files = [generator.generate_class_diagram(module_filter)]
            elif diagram_type == "object":
                files = [generator.generate_object_diagram(module_filter)]
            elif diagram_type == "component":
                files = [generator.generate_component_diagram()]
            elif diagram_type == "deployment":
                files = [generator.generate_deployment_diagram()]
            elif diagram_type == "usecase":
                files = [generator.generate_use_case_diagram()]
            elif diagram_type == "role_hierarchy":
                files = [generator.generate_role_hierarchy_diagram()]
            elif diagram_type == "sequence":
                if scenario:
                    files = [generator.generate_sequence_diagram(scenario)]
                else:
                    files = [
                        generator.generate_sequence_diagram("student_registration"),
                        generator.generate_sequence_diagram("grade_submission"),
                        generator.generate_sequence_diagram("auth_login_flow"),
                        generator.generate_sequence_diagram("student_inscription_flow"),
                        generator.generate_sequence_diagram(
                            "dashboard_notifications_flow"
                        ),
                        generator.generate_sequence_diagram(
                            "dashboard_payment_collection_flow"
                        ),
                    ]
            elif diagram_type == "activity":
                if scenario:
                    files = [generator.generate_activity_diagram(scenario)]
                else:
                    files = [
                        generator.generate_activity_diagram("auth_login"),
                        generator.generate_activity_diagram("student_enrollment"),
                        generator.generate_activity_diagram("teacher_grade_submission"),
                        generator.generate_activity_diagram("dean_course_management"),
                        generator.generate_activity_diagram(
                            "rector_payment_derogation"
                        ),
                        generator.generate_activity_diagram("quality_audit"),
                        generator.generate_activity_diagram("payment_collection"),
                        generator.generate_activity_diagram(
                            "student_service_scholarship"
                        ),
                        generator.generate_activity_diagram("alumni_event"),
                        generator.generate_activity_diagram(
                            "secretary_schedule_management"
                        ),
                        generator.generate_activity_diagram("super_admin_config"),
                        generator.generate_activity_diagram("exam_session_creation"),
                        generator.generate_activity_diagram("document_generation"),
                    ]
            else:
                return Response(
                    {"error": "Invalid diagram type"},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            return Response(
                {"message": f"Generated {len(files)} diagrams", "files": files},
                status=status.HTTP_200_OK,
            )
        except Exception as e:
            return Response(
                {"error": "Failed to generate diagrams", "details": str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )


class ModelStatsView(APIView):
    """Get statistics about all models in the project"""

    def get(self, request):
        all_models = apps.get_models()

        stats = {
            "total_models": len(all_models),
            "models_by_app": {},
            "total_fields": 0,
            "models_by_service": {
                "foundational_service": 0,
                "core_service": 0,
                "dependent_service": 0,
            },
        }

        for model in all_models:
            app_label = model._meta.app_label

            for service in stats["models_by_service"].keys():
                if service in app_label:
                    stats["models_by_service"][service] += 1

            if app_label not in stats["models_by_app"]:
                stats["models_by_app"][app_label] = {"count": 0, "models": []}

            field_count = len(model._meta.get_fields())
            stats["total_fields"] += field_count

            relationships = {"foreign_keys": [], "many_to_many": [], "one_to_one": []}

            for field in model._meta.get_fields():
                if field.many_to_one:
                    relationships["foreign_keys"].append(
                        {
                            "field": field.name,
                            "related_model": field.related_model.__name__,
                        }
                    )
                elif field.many_to_many:
                    relationships["many_to_many"].append(
                        {
                            "field": field.name,
                            "related_model": field.related_model.__name__,
                        }
                    )
                elif field.one_to_one:
                    relationships["one_to_one"].append(
                        {
                            "field": field.name,
                            "related_model": field.related_model.__name__,
                        }
                    )

            stats["models_by_app"][app_label]["count"] += 1
            stats["models_by_app"][app_label]["models"].append(
                {
                    "name": model.__name__,
                    "fields": field_count,
                    "db_table": model._meta.db_table,
                    "relationships": relationships,
                }
            )

        return Response(stats)


class DiagramTypesView(APIView):
    """List all available diagram types and scenarios"""

    def get(self, request):
        return Response(
            {
                "diagram_types": [
                    {
                        "type": "class",
                        "description": "UML Class Diagram",
                        "requires_module": True,
                    },
                    {
                        "type": "object",
                        "description": "UML Object Diagram",
                        "requires_module": True,
                    },
                    {
                        "type": "component",
                        "description": "UML Component Diagram",
                        "requires_module": False,
                    },
                    {
                        "type": "deployment",
                        "description": "UML Deployment Diagram",
                        "requires_module": False,
                    },
                    {
                        "type": "usecase",
                        "description": "UML Use Case Diagram",
                        "requires_module": False,
                    },
                    {
                        "type": "role_hierarchy",
                        "description": "Role Hierarchy Diagram",
                        "requires_module": False,
                    },
                    {
                        "type": "sequence",
                        "description": "UML Sequence Diagram",
                        "requires_scenario": True,
                    },
                    {
                        "type": "activity",
                        "description": "UML Activity Diagram",
                        "requires_scenario": True,
                    },
                    {
                        "type": "all",
                        "description": "Generate all diagrams",
                        "requires_module": False,
                    },
                ],
                "sequence_scenarios": [
                    {
                        "name": "student_registration",
                        "description": "Student registration flow",
                    },
                    {
                        "name": "grade_submission",
                        "description": "Teacher grade submission flow",
                    },
                    {
                        "name": "auth_login_flow",
                        "description": "Authentication login flow",
                    },
                    {
                        "name": "student_inscription_flow",
                        "description": "Student inscription flow",
                    },
                    {
                        "name": "dashboard_notifications_flow",
                        "description": "Dashboard notifications flow",
                    },
                    {
                        "name": "dashboard_payment_collection_flow",
                        "description": "Dashboard payment collection flow",
                    },
                ],
                "activity_scenarios": [
                    {
                        "name": "auth_login",
                        "category": "Authentication",
                        "description": "User login with 2FA",
                    },
                    {
                        "name": "auth_register",
                        "category": "Authentication",
                        "description": "User registration",
                    },
                    {
                        "name": "auth_password_reset",
                        "category": "Authentication",
                        "description": "Password reset flow",
                    },
                    {
                        "name": "student_enrollment",
                        "category": "Student",
                        "description": "Student enrollment process",
                    },
                    {
                        "name": "student_course_registration",
                        "category": "Student",
                        "description": "Course registration",
                    },
                    {
                        "name": "student_document_request",
                        "category": "Student",
                        "description": "Document request",
                    },
                    {
                        "name": "teacher_grade_submission",
                        "category": "Teacher",
                        "description": "Grade submission",
                    },
                    {
                        "name": "teacher_attendance",
                        "category": "Teacher",
                        "description": "Attendance marking",
                    },
                    {
                        "name": "dean_course_management",
                        "category": "Dean",
                        "description": "Course and teacher management",
                    },
                    {
                        "name": "dean_faculty_management",
                        "category": "Dean",
                        "description": "Faculty management",
                    },
                    {
                        "name": "rector_payment_derogation",
                        "category": "Rector",
                        "description": "Payment derogation approval",
                    },
                    {
                        "name": "rector_program_approval",
                        "category": "Rector",
                        "description": "Program approval",
                    },
                    {
                        "name": "quality_audit",
                        "category": "Quality Director",
                        "description": "Quality audit process",
                    },
                    {
                        "name": "quality_satisfaction_survey",
                        "category": "Quality Director",
                        "description": "Satisfaction survey",
                    },
                    {
                        "name": "payment_collection",
                        "category": "Collection Agent",
                        "description": "Payment collection",
                    },
                    {
                        "name": "payment_plan_creation",
                        "category": "Collection Agent",
                        "description": "Payment plan creation",
                    },
                    {
                        "name": "student_service_scholarship",
                        "category": "Student Services",
                        "description": "Scholarship application",
                    },
                    {
                        "name": "student_service_counseling",
                        "category": "Student Services",
                        "description": "Counseling session",
                    },
                    {
                        "name": "alumni_event",
                        "category": "Alumni",
                        "description": "Alumni event creation",
                    },
                    {
                        "name": "alumni_job_posting",
                        "category": "Alumni",
                        "description": "Job posting",
                    },
                    {
                        "name": "secretary_schedule_management",
                        "category": "Academic Secretary",
                        "description": "Schedule management",
                    },
                    {
                        "name": "super_admin_config",
                        "category": "Super Admin",
                        "description": "System configuration",
                    },
                    {
                        "name": "super_admin_university_setup",
                        "category": "Super Admin",
                        "description": "University setup",
                    },
                    {
                        "name": "academic_director_program_review",
                        "category": "Academic Director",
                        "description": "Program review",
                    },
                    {
                        "name": "exam_session_creation",
                        "category": "Exam",
                        "description": "Exam session creation",
                    },
                    {
                        "name": "document_generation",
                        "category": "Document",
                        "description": "Document generation",
                    },
                ],
            }
        )
