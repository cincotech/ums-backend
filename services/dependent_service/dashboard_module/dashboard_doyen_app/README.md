# DOYEN Dashboard Module

The DOYEN Dashboard Module provides comprehensive management tools for faculty deans to oversee academic and administrative operations.

## Features

### 1. Schedule Management
- Create, modify, and publish weekly schedules
- Assign courses to rooms and teachers
- Support for permanent and visiting professors

### 2. Teaching Progress Monitoring
- Track course progress percentage
- Monitor teaching compliance with academic calendar
- Review reports from professors and student delegates

### 3. Teacher Management
- Assign courses to permanent and visiting teachers
- Track teacher workload and hours
- Ensure workload equity and compliance

### 4. Academic Supervision
- Review student academic results
- Manage deliberation juries
- Validate student progression and diploma awards

### 5. Room Logistics Coordination
- Allocate rooms for courses
- Track room capacity and availability
- Communicate room needs to General Services

### 6. Program & Curriculum Management
- Create and update training programs (License, Master, Doctorate)
- Define Teaching Units (UE) / Modules
- Assign ECTS credits
- Configure validation and compensation rules

### 7. Student Group Structuring
- Assign students to appropriate groups
- Manage groups based on options or logistics constraints

### 8. Secretary Communication
- Send notes to academic secretary
- Track note resolution status

## API Endpoints

### Dashboard Overview
- `GET /dashboard/doyen/overview/` - Get dashboard statistics

### Schedule Management
- `GET /dashboard/doyen/schedules/` - List all schedules
- `POST /dashboard/doyen/schedules/` - Create new schedule
- `POST /dashboard/doyen/schedules/<id>/publish/` - Publish schedule

### Teaching Progress
- `GET /dashboard/doyen/teaching-progress/` - Get teaching progress

### Teacher Workload
- `GET /dashboard/doyen/teacher-workload/` - Get teacher workload

### Student Groups
- `GET /dashboard/doyen/student-groups/` - List student groups
- `POST /dashboard/doyen/student-groups/` - Create student group

### Academic Programs
- `GET /dashboard/doyen/academic-programs/` - List programs
- `POST /dashboard/doyen/academic-programs/` - Create program

### Room Allocations
- `GET /dashboard/doyen/room-allocations/` - List room allocations
- `POST /dashboard/doyen/room-allocations/` - Allocate room

### Secretary Notes
- `GET /dashboard/doyen/secretary-notes/` - List notes
- `POST /dashboard/doyen/secretary-notes/` - Create note
- `POST /dashboard/doyen/secretary-notes/<id>/resolve/` - Mark note as resolved

## Models

### Schedule
Manages weekly schedules for faculty with status tracking (draft, published, archived).

### TeachingProgress
Tracks progress percentage of courses and teaching compliance.

### TeacherWorkload
Manages teacher workload, hours, and employment type (permanent/visiting).

### StudentGroup
Groups students by academic year and options.

### AcademicProgram
Defines training programs (License, Master, Doctorate).

### TeachingUnit
Maps courses to programs with credit assignments.

### RoomAllocation
Allocates rooms for scheduled courses.

### SecretaryNote
Communication channel with academic secretary.

## Usage Example

```python
from services.dependent_service.dashboard_module.dashboard_doyen_app.services import DoyenDashboardService

# Create a schedule
schedule = DoyenDashboardService.create_schedule(
    faculty=faculty_obj,
    academic_year="2024-2025",
    semester=1,
    created_by=user_obj
)

# Publish schedule
DoyenDashboardService.publish_schedule(schedule)

# Create academic program
program = DoyenDashboardService.create_academic_program(
    faculty=faculty_obj,
    program_name="Computer Science",
    level="license",
    description="CS Program"
)

# Get dashboard stats
stats = DoyenDashboardService.get_dashboard_stats(faculty_obj)
```
