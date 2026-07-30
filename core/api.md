# Core API Documentation

## Overview
RESTful API for managing academic data including universities, programs, departments, classes, modules, and courses.

## Base URL
```
http://localhost:8000/api/
```

## Authentication
API uses role-based access control. Roles defined in `roles.csv`.

## Endpoints

### Universities
- `GET /api/university/` - List all universities
- `GET /api/university/{id}/` - Get specific university
- `POST /api/university/` - Create new university
- `PUT /api/university/{id}/` - Update university
- `DELETE /api/university/{id}/` - Delete university

### Programs
- `GET /api/program/` - List all programs
- `GET /api/program/{id}/` - Get specific program
- `POST /api/program/` - Create new program
- `PUT /api/program/{id}/` - Update program
- `DELETE /api/program/{id}/` - Delete program

### Departments
- `GET /api/department/` - List all departments
- `GET /api/department/{id}/` - Get specific department
- `POST /api/department/` - Create new department
- `PUT /api/department/{id}/` - Update department
- `DELETE /api/department/{id}/` - Delete department

### Classes
- `GET /api/class/` - List all classes
- `GET /api/class/{id}/` - Get specific class
- `POST /api/class/` - Create new class
- `PUT /api/class/{id}/` - Update class
- `DELETE /api/class/{id}/` - Delete class

### Modules
- `GET /api/module/` - List all modules
- `GET /api/module/{id}/` - Get specific module
- `POST /api/module/` - Create new module
- `PUT /api/module/{id}/` - Update module
- `DELETE /api/module/{id}/` - Delete module

### Courses
- `GET /api/course/` - List all courses
- `GET /api/course/{id}/` - Get specific course
- `POST /api/course/` - Create new course
- `PUT /api/course/{id}/` - Update course
- `DELETE /api/course/{id}/` - Delete course

## Data Import
- `GET /api/import/courses/` - Import courses from `courses.xlsx`
- `GET /api/import/orientation/` - Import from `orientation_UB_2025-2026.json`
