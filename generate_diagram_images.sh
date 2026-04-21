#!/bin/bash
# Generate PNG and SVG images from all PlantUML diagrams

echo "=========================================="
echo "UMS Diagram Image Generator"
echo "=========================================="
echo ""

# Check if plantuml is installed
if ! command -v plantuml &> /dev/null; then
    echo "❌ PlantUML is not installed."
    echo ""
    echo "Install options:"
    echo "  Ubuntu/Debian: sudo apt-get install plantuml"
    echo "  macOS: brew install plantuml"
    echo "  Or download from: https://plantuml.com/download"
    echo ""
    exit 1
fi

echo "✓ PlantUML found"
echo ""

# Create output directories
mkdir -p docs/diagrams/png
mkdir -p docs/diagrams/svg

# Count total files
TOTAL=$(find docs/diagrams -name "*.puml" | wc -l)
echo "Found $TOTAL PlantUML files"
echo ""

# Generate PNG images
echo "Generating PNG images..."
plantuml -tpng -o "$(pwd)/docs/diagrams/png" docs/diagrams/**/*.puml docs/diagrams/*.puml 2>/dev/null
PNG_COUNT=$(find docs/diagrams/png -name "*.png" | wc -l)
echo "✓ Generated $PNG_COUNT PNG images"

# Generate SVG images
echo "Generating SVG images..."
plantuml -tsvg -o "$(pwd)/docs/diagrams/svg" docs/diagrams/**/*.puml docs/diagrams/*.puml 2>/dev/null
SVG_COUNT=$(find docs/diagrams/svg -name "*.svg" | wc -l)
echo "✓ Generated $SVG_COUNT SVG images"

echo ""
echo "=========================================="
echo "✓ Image generation complete!"
echo "=========================================="
echo ""
echo "Output locations:"
echo "  PNG: docs/diagrams/png/"
echo "  SVG: docs/diagrams/svg/"
echo ""
