# Diagram Generation API Guide

## Overview
Comprehensive API for generating UML diagrams including class, sequence, activity, use case, component, deployment, and more.

## Endpoints

### 1. List Available Diagram Types
**GET** `/api/visualization/diagrams/types/`

Returns all available diagram types and scenarios.

**Response:**
```json
{
  "diagram_types": [
    {"type": "class", "description": "UML Class Diagram", "requires_module": true},
    {"type": "sequence", "description": "UML Sequence Diagram", "requires_scenario": true},
    {"type": "activity", "description": "UML Activity Diagram", "requires_scenario": true}
  ],
  "sequence_scenarios": [...],
  "activity_scenarios": [...]
}
```

### 2. Generate Diagrams
**POST** `/api/visualization/diagrams/generate/`

Generate specific or all diagrams.

**Request Body:**
```json
{
  "diagram_type": "activity",
  "scenario": "student_enrollment",
  "module": "student_module"
}
```

**Parameters:**
- `diagram_type` (string): Type of diagram to generate
  - `all` - Generate all diagrams
  - `class` - UML Class Diagram
  - `object` - UML Object Diagram
  - `component` - UML Component Diagram
  - `deployment` - UML Deployment Diagram
  - `usecase` - UML Use Case Diagram
  - `role_hierarchy` - Role Hierarchy Diagram
  - `sequence` - UML Sequence Diagram
  - `activity` - UML Activity Diagram

- `scenario` (string, optional): Specific scenario for sequence/activity diagrams
- `module` (string, optional): Filter by module for class/object diagrams

### 3. List Generated Diagrams
**GET** `/api/visualization/diagrams/`

List all generated diagram files.

### 4. Model Statistics
**GET** `/api/visualization/stats/`

Get statistics about all models in the project.

## Examples

### Generate All Diagrams
```bash
curl -X POST http://localhost:8000/api/visualization/diagrams/generate/ \
  -H "Content-Type: application/json" \
  -d '{"diagram_type": "all"}'
```

### Generate Specific Activity Diagram
```bash
curl -X POST http://localhost:8000/api/visualization/diagrams/generate/ \
  -H "Content-Type: application/json" \
  -d '{
    "diagram_type": "activity",
    "scenario": "auth_login"
  }'
```

### Generate All Activity Diagrams
```bash
curl -X POST http://localhost:8000/api/visualization/diagrams/generate/ \
  -H "Content-Type: application/json" \
  -d '{"diagram_type": "activity"}'
```

### Generate Sequence Diagram
```bash
curl -X POST http://localhost:8000/api/visualization/diagrams/generate/ \
  -H "Content-Type: application/json" \
  -d '{
    "diagram_type": "sequence",
    "scenario": "student_registration"
  }'
```

### Generate Class Diagram for Specific Module
```bash
curl -X POST http://localhost:8000/api/visualization/diagrams/generate/ \
  -H "Content-Type: application/json" \
  -d '{
    "diagram_type": "class",
    "module": "student_module"
  }'
```

## Available Scenarios

### Sequence Diagrams
- `student_registration` - Student registration flow
- `grade_submission` - Teacher grade submission flow
- `auth_login_flow` - Authentication login flow
- `student_inscription_flow` - Student inscription flow
- `dashboard_notifications_flow` - Dashboard notifications flow
- `dashboard_payment_collection_flow` - Dashboard payment collection flow

### Activity Diagrams

#### Authentication
- `auth_login` - User login with 2FA
- `auth_register` - User registration
- `auth_password_reset` - Password reset flow

#### Student
- `student_enrollment` - Student enrollment process
- `student_course_registration` - Course registration
- `student_document_request` - Document request

#### Teacher
- `teacher_grade_submission` - Grade submission
- `teacher_attendance` - Attendance marking

#### Dean
- `dean_course_management` - Course and teacher management
- `dean_faculty_management` - Faculty management

#### Rector
- `rector_payment_derogation` - Payment derogation approval
- `rector_program_approval` - Program approval

#### Quality Director
- `quality_audit` - Quality audit process
- `quality_satisfaction_survey` - Satisfaction survey

#### Collection Agent
- `payment_collection` - Payment collection
- `payment_plan_creation` - Payment plan creation

#### Student Services
- `student_service_scholarship` - Scholarship application
- `student_service_counseling` - Counseling session

#### Alumni
- `alumni_event` - Alumni event creation
- `alumni_job_posting` - Job posting

#### Academic Secretary
- `secretary_schedule_management` - Schedule management

#### Super Admin
- `super_admin_config` - System configuration
- `super_admin_university_setup` - University setup

#### Academic Director
- `academic_director_program_review` - Program review

#### Exam & Document
- `exam_session_creation` - Exam session creation
- `document_generation` - Document generation

## Response Format

**Success Response:**
```json
{
  "message": "Generated 13 diagrams",
  "files": [
    "activity_diagram_auth_login.puml",
    "activity_diagram_student_enrollment.puml",
    "sequence_diagram_student_registration.puml"
  ]
}
```

**Error Response:**
```json
{
  "error": "Invalid diagram type",
  "details": "..."
}
```

## Output Location
All generated diagrams are saved to: `docs/diagrams/plantuml/`

## Viewing Diagrams
Use PlantUML viewer or convert to PNG/SVG:
```bash
plantuml docs/diagrams/plantuml/*.puml
```
