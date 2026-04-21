# UMS Visualization Module - Diagram Generation

This module provides comprehensive diagram generation for the University Management System (UMS).

## Features

### 1. Component Diagrams (7 Modules)
- Academic Module
- Financial Module
- Scheduling/Planning Module
- Notification Module
- Dashboard/Supervision Module
- User & Role Module
- Security Module

### 2. Package Diagrams
- Module organization and dependencies
- Service layer architecture
- App-level package structure

### 3. State Diagrams
- Student lifecycle states
- Payment states
- Course states
- Exam states
- Document request states
- Inscription states
- Derogation states
- Program approval states

### 4. Activity Diagrams (30+ Processes)

#### Authentication & Authorization
- Login flow
- Registration flow
- Password reset flow

#### Student Workflows
- Enrollment/Inscription
- Course registration
- Document requests

#### Teacher Workflows
- Grade submission
- Attendance marking

#### Dean Workflows
- Course management
- Faculty management

#### Rector Workflows
- Payment derogation approval
- Program approval

#### Quality Director Workflows
- Quality audit
- Satisfaction surveys

#### Financial Workflows
- Payment collection
- Payment plan creation

#### Student Services
- Scholarship management
- Counseling sessions

#### Alumni
- Event management
- Job postings

#### Administrative
- Schedule management
- System configuration

### 5. Sequence Diagrams
- Student registration flow
- Grade submission flow
- Authentication login flow
- Student inscription flow
- Dashboard notifications flow
- Payment collection flow

### 6. Traceability Matrix
- Use cases to API endpoints mapping
- Available in: Markdown, CSV, PlantUML formats

### 7. Database Schema Diagrams
- Entity Relationship Diagrams (ERD)
- Academic schema
- Student schema
- Financial schema
- Exam schema

### 8. Additional Diagrams
- Class diagrams
- Object diagrams
- Deployment diagrams
- Use case diagrams
- Role hierarchy diagrams

## Installation

Ensure the visualization module is included in your Django settings:

```python
INSTALLED_APPS = [
    # ...
    'services.dependent_service.visualization_module.diagram_app',
]
```

## Usage

### Generate All Diagrams

```bash
python manage.py generate_diagrams
```

### Generate Specific Diagram Types

```bash
# Activity diagrams only
python manage.py generate_diagrams --type activity

# Sequence diagrams only
python manage.py generate_diagrams --type sequence

# State diagrams only
python manage.py generate_diagrams --type state

# Package diagrams only
python manage.py generate_diagrams --type package

# Component diagrams only
python manage.py generate_diagrams --type component

# Database diagrams only
python manage.py generate_diagrams --type database

# Traceability matrix only
python manage.py generate_diagrams --type traceability
```

### Generate Module-Specific Diagrams

```bash
python manage.py generate_diagrams --module academic_module
python manage.py generate_diagrams --module student_module
```

## Programmatic Usage

```python
from services.dependent_service.visualization_module.diagram_app.master_diagram_generator import MasterDiagramGenerator

# Initialize generator
generator = MasterDiagramGenerator()

# Generate all diagrams
results = generator.generate_all_diagrams()

# Generate specific categories
activity_diagrams = generator.generate_activity_diagrams_by_category()
sequence_diagrams = generator.generate_sequence_diagrams_all()

# Generate for specific module
module_diagrams = generator.generate_module_specific('academic_module')

# Generate summary report
report = generator.generate_summary_report(results)
print(report)
```

## Output Structure

```
docs/diagrams/
├── plantuml/
│   ├── class_diagram_*.puml
│   ├── object_diagram_*.puml
│   ├── component_diagram.puml
│   ├── deployment_diagram.puml
│   ├── use_case_diagram.puml
│   ├── role_hierarchy_diagram.puml
│   ├── sequence_diagram_*.puml
│   ├── activity_diagram_*.puml
│   ├── components/
│   │   └── *_component_detail.puml
│   ├── states/
│   │   └── *_state.puml
│   └── packages/
│       └── *_package.puml
├── database/
│   ├── erd_*.puml
│   └── *_schema.puml
└── traceability/
    ├── traceability_matrix.md
    ├── traceability_matrix.csv
    └── traceability_matrix.puml
```

## Viewing Diagrams

### Using PlantUML

1. Install PlantUML: https://plantuml.com/download
2. Generate PNG/SVG from .puml files:

```bash
java -jar plantuml.jar docs/diagrams/**/*.puml
```

### Using VS Code

Install the PlantUML extension:
- Extension ID: `jebbs.plantuml`
- Preview diagrams directly in VS Code

### Using Online Tools

- PlantUML Online Server: http://www.plantuml.com/plantuml/uml/
- Copy and paste .puml content

## Customization

### Adding New Activity Diagrams

Edit `plantuml_generator.py` and add to the `processes` dictionary in `generate_activity_diagram()`:

```python
"my_new_process": [
    "@startuml",
    "start",
    ":Step 1;",
    ":Step 2;",
    "stop",
    "@enduml",
]
```

### Adding New State Diagrams

Edit `state_diagram_generator.py` and create a new method:

```python
def generate_my_entity_state(self):
    content = [
        "@startuml",
        "[*] --> State1",
        "State1 --> State2",
        "State2 --> [*]",
        "@enduml",
    ]
    filename = "my_entity_state.puml"
    (self.output_dir / filename).write_text("\n".join(content))
    return filename
```

### Adding New Sequence Diagrams

Edit `plantuml_generator.py` and add to the `scenarios` dictionary in `generate_sequence_diagram()`.

## Module Coverage

### 1. Academic Module
- University, Faculty, Department management
- Program and Course management
- Class and Academic Year management
- Grade and Result management

### 2. Financial Module
- Payment processing and tracking
- Fee structure management
- Derogation handling
- Scholarship management

### 3. Scheduling Module
- Schedule creation and management
- Timetable generation
- Attendance tracking

### 4. Notification Module
- Multi-channel notifications (Email, SMS, Push)
- Notification templates
- Queue management

### 5. Dashboard Module
- Analytics and reporting
- KPI tracking
- Visualization components

### 6. User & Role Module
- User management
- Role and permission management
- Authentication and authorization

### 7. Security Module
- Audit logging
- Access control
- Encryption services
- Threat detection

## Best Practices

1. **Regular Generation**: Regenerate diagrams after significant model changes
2. **Version Control**: Commit generated diagrams to track system evolution
3. **Documentation**: Use diagrams in technical documentation and onboarding
4. **Review**: Include diagram review in code review process
5. **Automation**: Integrate diagram generation in CI/CD pipeline

## Troubleshooting

### Issue: Diagrams not generating

**Solution**: Ensure all Django apps are properly configured in INSTALLED_APPS

### Issue: Missing models in diagrams

**Solution**: Run migrations first: `python manage.py migrate`

### Issue: PlantUML syntax errors

**Solution**: Validate .puml files at http://www.plantuml.com/plantuml/uml/

## Contributing

When adding new features:
1. Update relevant diagram generators
2. Add new activity/sequence diagrams for new workflows
3. Update traceability matrix with new endpoints
4. Regenerate all diagrams
5. Update this README

## License

Part of the UMS Backend System
