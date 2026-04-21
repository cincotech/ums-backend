#!/usr/bin/env python3
"""
Standalone test script for diagram generators
This can be run without Django setup to test the basic functionality
"""

import sys
from pathlib import Path

# Add project to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent.parent))


def test_state_diagrams():
    """Test state diagram generation"""
    from services.dependent_service.visualization_module.diagram_app.state_diagram_generator import (
        StateDiagramGenerator,
    )

    print("Testing State Diagram Generator...")
    gen = StateDiagramGenerator()
    results = gen.generate_all()
    print(f"✓ Generated {len(results)} state diagrams:")
    for r in results:
        print(f"  - {r}")
    return results


def test_package_diagrams():
    """Test package diagram generation"""
    from services.dependent_service.visualization_module.diagram_app.package_diagram_generator import (
        PackageDiagramGenerator,
    )

    print("\nTesting Package Diagram Generator...")
    gen = PackageDiagramGenerator()
    results = gen.generate_all()
    print(f"✓ Generated {len(results)} package diagrams:")
    for r in results:
        print(f"  - {r}")
    return results


def test_component_diagrams():
    """Test component diagram generation"""
    from services.dependent_service.visualization_module.diagram_app.component_detail_generator import (
        ComponentDetailGenerator,
    )

    print("\nTesting Component Detail Generator...")
    gen = ComponentDetailGenerator()
    results = gen.generate_all()
    print(f"✓ Generated {len(results)} component diagrams:")
    for r in results:
        print(f"  - {r}")
    return results


def test_traceability_matrix():
    """Test traceability matrix generation"""
    from services.dependent_service.visualization_module.diagram_app.traceability_matrix_generator import (
        TraceabilityMatrixGenerator,
    )

    print("\nTesting Traceability Matrix Generator...")
    gen = TraceabilityMatrixGenerator()
    results = gen.generate_matrix()
    print(f"✓ Generated traceability matrix in {len(results)} formats:")
    for r in results:
        print(f"  - {r}")
    return results


if __name__ == "__main__":
    print("=" * 70)
    print("UMS Diagram Generator - Standalone Test")
    print("=" * 70)
    print()

    try:
        test_state_diagrams()
        test_package_diagrams()
        test_component_diagrams()
        test_traceability_matrix()

        print()
        print("=" * 70)
        print("✓ All tests passed successfully!")
        print("=" * 70)
        print()
        print("Generated files are in:")
        print("  - docs/diagrams/plantuml/states/")
        print("  - docs/diagrams/plantuml/packages/")
        print("  - docs/diagrams/plantuml/components/")
        print("  - docs/diagrams/traceability/")

    except Exception as e:
        print(f"\n✗ Error: {e}")
        import traceback

        traceback.print_exc()
        sys.exit(1)
