# Dean (DOYEN) Dashboard API Documentation

This module provides comprehensive dashboard functionality for the Dean (DOYEN) role, enabling them to manage academic operations, monitor teaching progress, coordinate schedules, and oversee faculty activities.

## Table of Contents
- [Features](#features)
- [API Endpoints](#api-endpoints)
- [Models](#models)
- [Usage Examples](#usage-examples)

## Features

The Dean Dashboard provides the following capabilities based on the DOYEN use cases:

### 1. Planification et Création des Horaires (Schedule Planning and Creation)
- View and manage timetables for all levels
- Monitor room allocations and assignments
- Track course attributions to professors (permanent and visiting)

### 2. Suivi du Déroulement des Enseignements (Teaching Progress Monitoring)
- Monitor teaching progress for all courses
- View detailed progress reports by course and teacher
- Track delivered vs planned hours
- Verify compliance with academic calendar

### 3. Gestion des Enseignants (Teacher Management)
- Manage teacher workloads (permanent and visiting)
- Track teaching hours and assignments
- Ensure equity and compliance in workload distribution
- View teacher attribution details

### 4. Supervision de la Scolarité (Academic Supervision)
- View academic statistics and metrics
- Monitor student enrollment and results
- Access information for deliberation juries

### 5. Coordination Logistique des Salles (Room Logistics Coordination)
- View room utilization reports
- Monitor room allocation efficiency
- Track capacity and occupancy

### 6. Remarques au Secrétaire (Secretary Notes)
- Create and manage notes for the academic secretary
- Report errors and issues for verification
- Track resolved and pending issues

### 7. Gestion des Programmes et Curricula (Program and Curriculum Management)
- View course attributions
- Monitor academic programs (License, Master, Doctorate)
- Track Teaching Units (UE) and credits (ECTS)

### 8. Structuration des Groupes (Group Structure)
- Monitor student group assignments
- View group distributions

## API Endpoints

Base URL: `/api/dashboard/doyen/`

### Teaching Progress

#### List Teaching Progress
```
GET /teaching-progress/
```
**Parameters:** `faculty`, `attribution`, `submitted_by`, `search`, `ordering`

**Response:**
```json
{
  "status": "success",
  "data": [{
    "id": "uuid",
    "course_name": "Introduction to Programming",
    "course_code": "CS101",
    "teacher_name": "John Doe",
    "progress_percentage": "75.50",
    "academic_year": "2024-2025"
  }]
}
```

#### Bulk Update Teaching Progress
```
POST /teaching-progress/bulk_update/
Body: {"faculty_id": "uuid", "academic_year_id": "uuid"}
```

### Teacher Workload

#### List Teacher Workloads
```
GET /teacher-workload/
```
**Parameters:** `faculty`, `teacher`, `academic_year`, `is_permanent`, `search`, `ordering`

#### Create/Update Teacher Workload
```
POST /teacher-workload/
Body: {
  "teacher": "uuid",
  "faculty": "uuid",
  "academic_year": "uuid",
  "total_hours": 120,
  "is_permanent": true
}
```

#### Get Workload Summary
```
GET /teacher-workload/summary/?faculty_id={uuid}&academic_year_id={uuid}
```

**Response:**
```json
{
  "status": "success",
  "data": [{
    "teacher_name": "John Doe",
    "total_hours": 120,
    "assigned_hours": 95.50,
    "workload_percentage": 79.58,
    "status": "Balanced"
  }]
}
```

### Secretary Notes

#### List Secretary Notes
```
GET /secretary-notes/
```
**Parameters:** `faculty`, `is_resolved`, `created_by`, `search`

#### Create Secretary Note
```
POST /secretary-notes/
Body: {
  "faculty": "uuid",
  "subject": "Registration Error",
  "message": "Please verify student data..."
}
```

#### Mark as Resolved/Unresolved
```
POST /secretary-notes/{id}/mark_resolved/
POST /secretary-notes/{id}/mark_unresolved/
```

### Course Attributions

#### List Course Attributions
```
GET /course-attributions/
```
**Parameters:** `course`, `principal_teacher`, `academic_year`, `status_principal_teacher`

#### Get by Teacher/Course
```
GET /course-attributions/by_teacher/?teacher_id={uuid}
GET /course-attributions/by_course/?course_id={uuid}
```

### Dashboard Statistics

#### Get Dashboard Stats
```
GET /stats/?faculty_id={uuid}&academic_year_id={uuid}
```

**Response:**
```json
{
  "status": "success",
  "data": {
    "total_timetables": 45,
    "teaching_progress_avg": 78.45,
    "total_teachers": 25,
    "permanent_teachers": 18,
    "visiting_teachers": 7,
    "total_attributions": 120,
    "pending_attributions": 8,
    "total_students": 450,
    "active_courses": 85
  }
}
```

### Reports

#### Timetable Overview
```
GET /timetable/overview/?faculty_id={uuid}&academic_year_id={uuid}
```

#### Teaching Progress Report
```
GET /reports/teaching-progress/?faculty_id={uuid}&academic_year_id={uuid}
```

#### Attribution Statistics
```
GET /stats/attributions/?faculty_id={uuid}&academic_year_id={uuid}
```

#### Room Utilization Report
```
GET /reports/room-utilization/?faculty_id={uuid}&academic_year_id={uuid}
```

## Models

### TeachingProgress
Tracks teaching progress for each course attribution.

**Fields:** `attribution`, `faculty`, `progress_percentage`, `last_updated`, `submitted_by`

**Methods:** `update_progress_from_timetable()` - Recalculates progress from activity reports

### TeacherWorkload
Tracks teacher workload per academic year.

**Fields:** `faculty`, `teacher`, `academic_year`, `total_hours`, `assigned_hours`, `is_permanent`

**Methods:** `update_from_progress()` - Updates assigned hours from teaching progress

### SecretaryNote
Notes from Dean to academic secretary.

**Fields:** `faculty`, `subject`, `message`, `created_by`, `created_date`, `is_resolved`

## Usage Examples

### Get Dashboard Overview
```python
import requests

response = requests.get(
    "http://api.example.com/api/dashboard/doyen/stats/",
    params={"faculty_id": "uuid", "academic_year_id": "uuid"},
    headers={"Authorization": "Bearer token"}
)
stats = response.json()
```

### Create Secretary Note
```python
response = requests.post(
    "http://api.example.com/api/dashboard/doyen/secretary-notes/",
    json={
        "faculty": "uuid",
        "subject": "Registration Error",
        "message": "Please verify..."
    },
    headers={"Authorization": "Bearer token"}
)
```

### Update All Teaching Progress
```python
response = requests.post(
    "http://api.example.com/api/dashboard/doyen/teaching-progress/bulk_update/",
    json={"faculty_id": "uuid", "academic_year_id": "uuid"},
    headers={"Authorization": "Bearer token"}
)
```

## Permissions

All endpoints require the `dean` role (enforced by `IsDean` permission).

## Notes

- All UUIDs as strings
- Dates in ISO 8601 format (YYYY-MM-DD)
- `academic_year_id` is optional (defaults to current year)
- Progress percentages auto-calculated
- Assigned hours auto-calculated from timetable data
