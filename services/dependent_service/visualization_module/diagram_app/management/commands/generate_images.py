import subprocess
from pathlib import Path

from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = "Generate PNG and SVG images from PlantUML diagrams"

    def add_arguments(self, parser):
        parser.add_argument(
            "--format",
            type=str,
            choices=["png", "svg", "both"],
            default="both",
            help="Image format to generate",
        )

    def handle(self, *args, **options):
        format_type = options.get("format")

        self.stdout.write("=" * 60)
        self.stdout.write(self.style.SUCCESS("UMS Diagram Image Generator"))
        self.stdout.write("=" * 60)
        self.stdout.write("")

        # Check if plantuml is available
        try:
            subprocess.run(
                ["plantuml", "-version"],
                capture_output=True,
                check=True,
            )
            self.stdout.write(self.style.SUCCESS("✓ PlantUML found"))
        except (subprocess.CalledProcessError, FileNotFoundError):
            self.stdout.write(
                self.style.ERROR("❌ PlantUML is not installed or not in PATH")
            )
            self.stdout.write("")
            self.stdout.write("Install options:")
            self.stdout.write("  Ubuntu/Debian: sudo apt-get install plantuml")
            self.stdout.write("  macOS: brew install plantuml")
            self.stdout.write("  Or download from: https://plantuml.com/download")
            return

        # Find all .puml files
        base_path = Path("docs/diagrams")
        puml_files = list(base_path.rglob("*.puml"))
        self.stdout.write(f"\nFound {len(puml_files)} PlantUML files")
        self.stdout.write("")

        # Create output directories
        png_dir = base_path / "png"
        svg_dir = base_path / "svg"
        png_dir.mkdir(parents=True, exist_ok=True)
        svg_dir.mkdir(parents=True, exist_ok=True)

        # Generate images
        if format_type in ["png", "both"]:
            self.stdout.write("Generating PNG images...")
            self._generate_images(puml_files, "png", png_dir)

        if format_type in ["svg", "both"]:
            self.stdout.write("Generating SVG images...")
            self._generate_images(puml_files, "svg", svg_dir)

        self.stdout.write("")
        self.stdout.write("=" * 60)
        self.stdout.write(self.style.SUCCESS("✓ Image generation complete!"))
        self.stdout.write("=" * 60)
        self.stdout.write("")
        self.stdout.write("Output locations:")
        if format_type in ["png", "both"]:
            png_count = len(list(png_dir.glob("*.png")))
            self.stdout.write(f"  PNG ({png_count} files): {png_dir}/")
        if format_type in ["svg", "both"]:
            svg_count = len(list(svg_dir.glob("*.svg")))
            self.stdout.write(f"  SVG ({svg_count} files): {svg_dir}/")
        self.stdout.write("")

    def _generate_images(self, puml_files, format_type, output_dir):
        """Generate images for all PlantUML files"""
        success_count = 0
        error_count = 0

        for puml_file in puml_files:
            try:
                subprocess.run(
                    [
                        "plantuml",
                        f"-t{format_type}",
                        "-o",
                        str(output_dir.absolute()),
                        str(puml_file),
                    ],
                    capture_output=True,
                    check=True,
                )
                success_count += 1
            except subprocess.CalledProcessError:
                error_count += 1
                self.stdout.write(
                    self.style.WARNING(f"  ⚠ Failed to generate: {puml_file.name}")
                )

        self.stdout.write(
            self.style.SUCCESS(
                f"✓ Generated {success_count} {format_type.upper()} images"
            )
        )
        if error_count > 0:
            self.stdout.write(self.style.WARNING(f"⚠ {error_count} files failed"))
