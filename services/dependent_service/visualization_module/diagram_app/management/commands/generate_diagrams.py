from django.core.management.base import BaseCommand

from services.dependent_service.visualization_module.diagram_app.master_diagram_generator import (
    MasterDiagramGenerator,
)


class Command(BaseCommand):
    help = "Generate all UML diagrams for the UMS system"

    def add_arguments(self, parser):
        parser.add_argument(
            "--module",
            type=str,
            help="Generate diagrams for a specific module only",
        )
        parser.add_argument(
            "--type",
            type=str,
            choices=[
                "all",
                "activity",
                "sequence",
                "state",
                "package",
                "component",
                "database",
                "traceability",
            ],
            default="all",
            help="Type of diagrams to generate",
        )

    def handle(self, *args, **options):
        generator = MasterDiagramGenerator()
        module = options.get("module")
        diagram_type = options.get("type")

        self.stdout.write(self.style.SUCCESS("Starting diagram generation..."))

        if module:
            self.stdout.write(f"Generating diagrams for module: {module}")
            results = generator.generate_module_specific(module)
        elif diagram_type == "activity":
            self.stdout.write("Generating activity diagrams...")
            results = generator.generate_activity_diagrams_by_category()
        elif diagram_type == "sequence":
            self.stdout.write("Generating sequence diagrams...")
            results = generator.generate_sequence_diagrams_all()
        elif diagram_type == "state":
            self.stdout.write("Generating state diagrams...")
            results = {"state": generator.state_gen.generate_all()}
        elif diagram_type == "package":
            self.stdout.write("Generating package diagrams...")
            results = {"package": generator.package_gen.generate_all()}
        elif diagram_type == "component":
            self.stdout.write("Generating component diagrams...")
            results = {"component": generator.component_detail_gen.generate_all()}
        elif diagram_type == "database":
            self.stdout.write("Generating database diagrams...")
            results = {"database": generator.db_schema_gen.generate_all()}
        elif diagram_type == "traceability":
            self.stdout.write("Generating traceability matrix...")
            results = {"traceability": generator.traceability_gen.generate_matrix()}
        else:
            self.stdout.write("Generating all diagrams...")
            results = generator.generate_all_diagrams()

        # Generate summary report
        report = generator.generate_summary_report(results)
        self.stdout.write("\n" + report)

        self.stdout.write(
            self.style.SUCCESS("\n✓ Diagram generation completed successfully!")
        )
