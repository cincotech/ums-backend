from pathlib import Path


class DynamicComponentGenerator:
    """Generate component diagrams based on actual module structure"""

    def __init__(self, output_dir="docs/diagrams/plantuml/components"):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.services_path = Path("services")

    def _get_apps_in_module(self, module_path):
        """Get all app directories in a module"""
        apps = []
        if not module_path.exists():
            return apps

        for item in module_path.iterdir():
            if (
                item.is_dir()
                and item.name.endswith("_app")
                and not item.name.startswith("__")
            ):
                apps.append(item.name)
        return sorted(apps)

    def _get_all_modules(self):
        """Get all modules organized by service"""
        modules = {}

        for service_dir in self.services_path.iterdir():
            if service_dir.is_dir() and service_dir.name.endswith("_service"):
                service_name = service_dir.name
                modules[service_name] = []

                for module_dir in service_dir.iterdir():
                    if module_dir.is_dir() and module_dir.name.endswith("_module"):
                        modules[service_name].append(module_dir)

        return modules

    def generate_module_component(self, module_path):
        """Generate component diagram for a specific module"""
        module_name = module_path.name
        apps = self._get_apps_in_module(module_path)

        if not apps:
            return None

        content = [
            "@startuml",
            f"package {module_name} {{",
        ]

        for app in apps:
            content.append(f"  component {app}")

        content.append("}")
        content.append("@enduml")

        filename = f"{module_name}_component_detail.puml"
        (self.output_dir / filename).write_text("\n".join(content))
        return filename

    def generate_all_components(self):
        """Generate component diagrams for all modules"""
        modules = self._get_all_modules()
        generated = []

        for service_name, module_paths in modules.items():
            for module_path in module_paths:
                filename = self.generate_module_component(module_path)
                if filename:
                    generated.append(filename)

        return generated

    def generate_package_diagrams(self):
        """Generate package diagrams for all modules"""
        modules = self._get_all_modules()
        generated = []

        for service_name, module_paths in modules.items():
            for module_path in module_paths:
                filename = self._generate_module_package(module_path)
                if filename:
                    generated.append(filename)

        # Generate overview
        overview = self._generate_packages_overview(modules)
        generated.append(overview)

        return generated

    def _generate_module_package(self, module_path):
        """Generate package diagram for a specific module"""
        module_name = module_path.name
        apps = self._get_apps_in_module(module_path)

        if not apps:
            return None

        output_dir = Path("docs/diagrams/plantuml/packages")
        output_dir.mkdir(parents=True, exist_ok=True)

        content = [
            "@startuml",
            f"package {module_name} {{",
        ]

        for app in apps:
            content.append(f"  package {app}")

        content.append("}")
        content.append("@enduml")

        filename = f"{module_name}_package.puml"
        (output_dir / filename).write_text("\n".join(content))
        return filename

    def _generate_packages_overview(self, modules):
        """Generate overview package diagram"""
        output_dir = Path("docs/diagrams/plantuml/packages")
        output_dir.mkdir(parents=True, exist_ok=True)

        content = [
            "@startuml",
            "",
        ]

        for service_name, module_paths in sorted(modules.items()):
            content.append(f"package {service_name} {{")
            for module_path in sorted(module_paths, key=lambda x: x.name):
                content.append(f"  package {module_path.name}")
            content.append("}")
            content.append("")

        content.append("foundational_service --> core_service")
        content.append("core_service --> dependent_service")
        content.append("@enduml")

        filename = "all_modules_package.puml"
        (output_dir / filename).write_text("\n".join(content))
        return filename
