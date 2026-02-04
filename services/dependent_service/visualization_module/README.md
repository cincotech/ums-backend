# Visualization Module - UML Diagrams

Generate UML diagrams using PlantUML and Django-Extensions.

## Quick Start

```bash
./generate_all_diagrams.sh
```

## UML Diagrams Supported

### PlantUML (Python-based)
- **Class Diagram**: Models with fields and relationships
- **Object Diagram**: Object instances
- **Use Case Diagram**: System actors and use cases
- **Sequence Diagram**: Interaction flows
- **Activity Diagram**: Process workflows
- **Component Diagram**: System architecture
- **Deployment Diagram**: Infrastructure layout

### Django-Extensions
- **Graph Models**: Visual model relationships

## Commands

### Generate Specific UML Diagram
```bash
# All diagrams
python manage.py generate_diagrams --type=all

# Specific type
python manage.py generate_diagrams --type=class
python manage.py generate_diagrams --type=usecase
python manage.py generate_diagrams --type=sequence
python manage.py generate_diagrams --type=activity
python manage.py generate_diagrams --type=component
python manage.py generate_diagrams --type=deployment
python manage.py generate_diagrams --type=object

# Filter by module
python manage.py generate_diagrams --type=class --module=core_service
```

### Django-Extensions
```bash
# Complete graph
python manage.py graph_models -a -g -o complete.png

# Specific apps
python manage.py graph_models user_app student_profile_app -g -o users.png

# Shell with auto-imports
python manage.py shell_plus
```

## API Endpoints

```bash
# Get stats
curl http://localhost:8000/api/visualization/stats/

# List diagrams
curl http://localhost:8000/api/visualization/diagrams/

# Generate diagram
curl -X POST http://localhost:8000/api/visualization/diagrams/generate/ \
  -H "Content-Type: application/json" \
  -d '{"diagram_type": "class", "module": "core_service"}'
```

## Output

```
docs/diagrams/
├── plantuml/
│   ├── class_diagram_all.puml
│   ├── use_case_diagram.puml
│   ├── sequence_diagram_student_registration.puml
│   ├── activity_diagram_student_enrollment.puml
│   ├── component_diagram.puml
│   ├── deployment_diagram.puml
│   └── object_diagram_all.puml
├── png/                    # PNG exports (if plantuml installed)
├── svg/                    # SVG exports (if plantuml installed)
└── *.png                   # Django-extensions graphs
```

## Installation

```bash
# System dependencies
sudo apt-get install graphviz plantuml  # Ubuntu/Debian
brew install graphviz plantuml          # macOS

# Python packages (already installed)
# django-extensions, graphviz
```

## View PlantUML Online

Visit: http://www.plantuml.com/plantuml/uml/
