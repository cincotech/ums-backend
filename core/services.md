# Core Services Documentation

## 1. Data Import Service (`import_data.py`)
**Purpose**: Import academic data from external files into the database.
**Sources**:
- `orientation_UB_2025-2026.json`: Universities, programs, departments
- `courses.xlsx`: Modules and courses
- `roles.csv`: User roles

**Usage**:
```bash
python import_data.py
```

## 2. Complete Object Creator (`create_complete_objects.py`)
**Purpose**: Generate complete academic entities (classes, modules) from raw data.
**Features**:
- Creates classes for each department
- Generates modules with proper credit hours
- Links modules to departments

**Usage**:
```bash
python create_complete_objects.py
```

## 3. Timetable Generator (`create_timetable_data.py`)
**Purpose**: Create academic schedules and timetables.
**Features**:
- Generates class schedules
- Assigns rooms to courses
- Handles time conflicts

**Usage**:
```bash
python create_timetable_data.py
```

## 4. Room Management (`create_room_objects.py`)
**Purpose**: Create and manage classroom objects.
**Features**:
- Room creation with capacity
- Room type classification
- Building assignment

Usage:
```bash
python create_room_objects.py
```

## 5. Attendance System (`simple_attendance.py`)
**Purpose**: Track student attendance for courses.
**Features**:
- Attendance recording
- Student presence tracking
- Reporting

Usage:
```bash
python simple_attendance.py
```

## 6. Health Check (`core/health_check.py`)
**Purpose**: Monitor backend service health.
**Endpoint**: `GET /api/health/`
**Returns**: Service status, database connectivity, uptime

## Utility Scripts

### Database Management (`dbmanage.py`)
- Run migrations
- Create superusers
- Reset database

### Fix Scripts
- `fix_surplus.py`: Correct surplus data entries
- `fix_attribution_data.py`: Fix attribution data inconsistencies

### Import Modules Courses (`import_modules_courses.py`)
- Specialized import for module-course relationships
- Handles complex mappings from Excel

## AI Integration
**OmniRoute Configuration** (`config.toml`):
- Model: `omniroute`
- Provider: `OmniRoute` (local server at `http://localhost:20128/api/v1`)
- Reasoning Effort: `max`
- API Key: `OPENAI_API_KEY` environment variable

## Logging
- Log files stored in `/ums-backend/logs/`
- Key logs:
  - `student_profile.dot`: Student profile operations
  - General application logs in `logs/` directory
