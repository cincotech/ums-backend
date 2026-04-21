from django.core.management.base import BaseCommand

from services.dependent_service.visualization_module.diagram_app.dynamic_component_generator import (
    DynamicComponentGenerator,
)


class Command(BaseCommand):
    help = "Generate component diagrams based on actual module structure"

    def add_arguments(self, parser):
        parser.add_argument(
            "--type",
            type=str,
            choices=["component", "package", "both"],
            default="both",
            help="Type of diagrams to generate",
        )

    def handle(self, *args, **options):
        diagram_type = options.get("type")

        self.stdout.write("=" * 60)
        self.stdout.write(self.style.SUCCESS("Dynamic Diagram Generator"))
        self.stdout.write("=" * 60)
        self.stdout.write("")

        generator = DynamicComponentGenerator()

        if diagram_type in ["component", "both"]:
            self.stdout.write("Generating component diagrams...")
            results = generator.generate_all_components()
            self.stdout.write(f"✓ Generated {len(results)} component diagrams")

        if diagram_type in ["package", "both"]:
            self.stdout.write("\nGenerating package diagrams...")
            results = generator.generate_package_diagrams()
            self.stdout.write(f"✓ Generated {len(results)} package diagrams")

        self.stdout.write("")
        self.stdout.write("=" * 60)
        self.stdout.write(self.style.SUCCESS("✓ Complete!"))
        self.stdout.write("=" * 60)
