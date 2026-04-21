from django.core.management.base import BaseCommand

from services.dependent_service.visualization_module.diagram_app.dynamic_flow_generator import (
    DynamicFlowGenerator,
)


class Command(BaseCommand):
    help = "Generate sequence and activity diagrams from actual views"

    def add_arguments(self, parser):
        parser.add_argument(
            "--type",
            type=str,
            choices=["sequence", "activity", "both"],
            default="both",
            help="Type of flow diagrams to generate",
        )

    def handle(self, *args, **options):
        diagram_type = options.get("type")

        self.stdout.write("=" * 60)
        self.stdout.write(self.style.SUCCESS("Dynamic Flow Diagram Generator"))
        self.stdout.write("=" * 60)
        self.stdout.write("")

        generator = DynamicFlowGenerator()

        if diagram_type in ["sequence", "both"]:
            self.stdout.write("Generating sequence diagrams from views...")
            results = generator.generate_all_sequences()
            self.stdout.write(f"✓ Generated {len(results)} sequence diagrams")

        if diagram_type in ["activity", "both"]:
            self.stdout.write("\nGenerating activity diagrams from views...")
            results = generator.generate_all_activities()
            self.stdout.write(f"✓ Generated {len(results)} activity diagrams")

        self.stdout.write("")
        self.stdout.write("=" * 60)
        self.stdout.write(self.style.SUCCESS("✓ Complete!"))
        self.stdout.write("=" * 60)
