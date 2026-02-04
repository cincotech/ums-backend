from django.core.management.base import BaseCommand

from ...plantuml_generator import PlantUMLGenerator


class Command(BaseCommand):
    help = "Generate UML diagrams using PlantUML"

    def add_arguments(self, parser):
        parser.add_argument("--output", type=str, default="docs/diagrams/plantuml")
        parser.add_argument("--module", type=str, help="Filter by module")
        parser.add_argument(
            "--type",
            type=str,
            choices=[
                "all",
                "class",
                "object",
                "component",
                "deployment",
                "usecase",
                "sequence",
                "activity",
            ],
            default="all",
        )

    def handle(self, *args, **options):
        generator = PlantUMLGenerator(options["output"])
        diagram_type = options["type"]
        module_filter = options.get("module")

        self.stdout.write(self.style.SUCCESS("🎨 Generating PlantUML diagrams..."))

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
        elif diagram_type == "sequence":
            files = [
                generator.generate_sequence_diagram("student_registration"),
                generator.generate_sequence_diagram("grade_submission"),
            ]
        elif diagram_type == "activity":
            files = [
                generator.generate_activity_diagram("student_enrollment"),
                generator.generate_activity_diagram("grade_processing"),
            ]

        for f in files:
            self.stdout.write(f"  ✓ {f}")

        self.stdout.write(self.style.SUCCESS(f"✅ Generated {len(files)} diagrams"))
