"""
Example usage of the UMS Diagram Generators

This script demonstrates how to use the diagram generators programmatically.
"""

from services.dependent_service.visualization_module.diagram_app import (
    ComponentDetailGenerator,
    DatabaseSchemaGenerator,
    MasterDiagramGenerator,
    PackageDiagramGenerator,
    PlantUMLGenerator,
    StateDiagramGenerator,
    TraceabilityMatrixGenerator,
)


def generate_all_diagrams():
    """Generate all diagrams using the master generator"""
    generator = MasterDiagramGenerator()
    results = generator.generate_all_diagrams()
    report = generator.generate_summary_report(results)
    print(report)
    return results


def generate_specific_module(module_name="academic_module"):
    """Generate diagrams for a specific module"""
    generator = MasterDiagramGenerator()
    results = generator.generate_module_specific(module_name)
    print(f"Generated diagrams for {module_name}:")
    for diagram_type, filename in results.items():
        print(f"  - {diagram_type}: {filename}")
    return results


def generate_activity_diagrams():
    """Generate all activity diagrams by category"""
    generator = MasterDiagramGenerator()
    results = generator.generate_activity_diagrams_by_category()
    print("Generated activity diagrams:")
    for category, files in results.items():
        print(f"  {category}: {len(files)} diagrams")
    return results


def generate_component_diagrams():
    """Generate detailed component diagrams for all modules"""
    generator = ComponentDetailGenerator()
    results = generator.generate_all()
    print(f"Generated {len(results)} component diagrams")
    return results


def generate_state_diagrams():
    """Generate state diagrams for all entities"""
    generator = StateDiagramGenerator()
    results = generator.generate_all()
    print(f"Generated {len(results)} state diagrams")
    return results


def generate_package_diagrams():
    """Generate package diagrams"""
    generator = PackageDiagramGenerator()
    results = generator.generate_all()
    print(f"Generated {len(results)} package diagrams")
    return results


def generate_database_diagrams():
    """Generate database schema diagrams"""
    generator = DatabaseSchemaGenerator()
    results = generator.generate_all()
    print(f"Generated {len(results)} database diagrams")
    return results


def generate_traceability_matrix():
    """Generate traceability matrix"""
    generator = TraceabilityMatrixGenerator()
    results = generator.generate_matrix()
    print(f"Generated traceability matrix in {len(results)} formats")
    return results


def generate_sequence_diagrams():
    """Generate all sequence diagrams"""
    generator = PlantUMLGenerator()
    scenarios = [
        "student_registration",
        "grade_submission",
        "auth_login_flow",
        "student_inscription_flow",
        "dashboard_notifications_flow",
        "dashboard_payment_collection_flow",
    ]
    results = []
    for scenario in scenarios:
        filename = generator.generate_sequence_diagram(scenario)
        results.append(filename)
        print(f"Generated: {filename}")
    return results


if __name__ == "__main__":
    print("=" * 60)
    print("UMS Diagram Generator - Example Usage")
    print("=" * 60)
    print()

    # Example 1: Generate all diagrams
    print("1. Generating all diagrams...")
    generate_all_diagrams()
    print()

    # Example 2: Generate for specific module
    print("2. Generating diagrams for academic module...")
    generate_specific_module("academic_module")
    print()

    # Example 3: Generate activity diagrams
    print("3. Generating activity diagrams...")
    generate_activity_diagrams()
    print()

    # Example 4: Generate component diagrams
    print("4. Generating component diagrams...")
    generate_component_diagrams()
    print()

    # Example 5: Generate state diagrams
    print("5. Generating state diagrams...")
    generate_state_diagrams()
    print()

    # Example 6: Generate traceability matrix
    print("6. Generating traceability matrix...")
    generate_traceability_matrix()
    print()

    print("=" * 60)
    print("All examples completed!")
    print("=" * 60)
