# Course Management System - Dashboard Doyen App

## Overview

The Course Management System provides comprehensive course administration capabilities for deans, including course statistics, enrollment tracking, performance metrics, and attribution management with deep integration with the attribution system.

## Architecture

### Components

1. **CourseManagementService** (`course_management_service.py`)
   - Core business logic for course operations
   - Handles data aggregation and calculations
   - Integrates with Attribution, Timetable, and Result models

2. **Serializers** (`course_management_serializers.py`)
   - Data validation and transformation
   - Nested serialization for related data
   - Response formatting

3. **Views** (`course_management_views.py`)
   - REST API endpoints
   - Permission handling
   - Query parameter processing

## API Endpoints

### Base URL: `/dashboard/doyen/courses/`

### Course ViewSet Endpoints

#### 1. List All Courses
```
GET /dashboard/doyen/courses/
```
Returns paginated list of courses for the dean's faculty.

**Query Parameters:**
- `academic_year_id` (optional): Filter by academic year

**Response:**
```json
{
  "count": 15,
  "next": null,
  "previous": null,
  "results": [
    {
      "id": "uuid",
      "course_name": "Introduction to Programming",
      "course_code": "CS101",
      "course_credit": 3,
      "class_name": "L1-CS",
      "department_name": "Computer Science",
      "faculty_name": "Faculty of Science",
      "attribution_count": 2
    }
  ]
}
```

#### 2. Get Course by Faculty
```
GET /dashboard/doyen/courses/by_faculty/
```
Get all courses for the dean's faculty with optional academic year filtering.

**Query Parameters:**
- `academic_year_id` (optional): Filter by academic year

**Response:**
```json
{
  "success": true,
  "message": "Faculty courses retrieved successfully",
  "data": [
    {
      "id": "uuid",
      "course_name": "Introduction to Programming",
      "course_code": "CS101",
      "course_credit": 3,
      "class_name": "L1-CS",
      "department_name": "Computer Science"
    }
  ]
}
```

#### 3. Get Course Statistics
```
GET /dashboard/doyen/courses/{id}/statistics/
```
Comprehensive statistics for a specific course including attributions, timetables, and delivery metrics.

**Query Parameters:**
- `academic_year_id` (optional): Filter by academic year

**Response:**
```json
{
  "success": true,
  "message": "Course statistics retrieved successfully",
  "data": {
    "course_id": "uuid",
    "course_name": "Introduction to Programming",
    "course_code": "CS101",
    "credits": 3,
    "total_attributions": 2,
    "accepted_attributions": 2,
    "pending_attributions": 0,
    "total_timetables": 4,
    "published_timetables": 3,
    "total_planned_hours": 60,
    "total_delivered_hours": 45,
    "avg_completion_rate": 75.0,
    "total_students": 120
  }
}
```

#### 4. Get Course Enrollment
```
GET /dashboard/doyen/courses/{id}/enrollment/
```
Enrollment statistics including gender distribution and class breakdown.

**Query Parameters:**
- `academic_year_id` (optional): Filter by academic year

**Response:**
```json
{
  "success": true,
  "message": "Course enrollment retrieved successfully",
  "data": {
    "course_id": "uuid",
    "course_name": "Introduction to Programming",
    "total_enrolled": 120,
    "male": 75,
    "female": 45,
    "by_class": [
      {
        "class_fk__class_name": "L1-CS",
        "count": 60
      },
      {
        "class_fk__class_name": "L1-IT",
        "count": 60
      }
    ]
  }
}
```

#### 5. Get Course Performance
```
GET /dashboard/doyen/courses/{id}/performance/
```
Performance metrics based on exam results.

**Query Parameters:**
- `academic_year_id` (optional): Filter by academic year

**Response:**
```json
{
  "success": true,
  "message": "Course performance retrieved successfully",
  "data": {
    "course_id": "uuid",
    "course_name": "Introduction to Programming",
    "total_results": 120,
    "average_mark": 72.5,
    "pass_rate": 85.0,
    "fail_rate": 15.0
  }
}
```

#### 6. Get Course Attributions
```
GET /dashboard/doyen/courses/{id}/attributions/
```
Detailed attribution status and teacher assignments.

**Query Parameters:**
- `academic_year_id` (optional): Filter by academic year

**Response:**
```json
{
  "success": true,
  "message": "Course attribution status retrieved successfully",
  "data": {
    "course_id": "uuid",
    "total_attributions": 2,
    "status_breakdown": {
      "pending": 0,
      "accepted": 2,
      "refused": 0,
      "with_substitute": 1
    },
    "attributions": [
      {
        "id": "uuid",
        "principal_teacher": "John Doe",
        "substitute_teacher": "Jane Smith",
        "status": "Accepted",
        "academic_year": "2023-2024"
      }
    ]
  }
}
```

#### 7. Get Course Activity Reports
```
GET /dashboard/doyen/courses/{id}/activity_reports/
```
All activity reports for course timetables.

**Query Parameters:**
- `academic_year_id` (optional): Filter by academic year

**Response:**
```json
{
  "success": true,
  "message": "Course activity reports retrieved successfully",
  "data": [
    {
      "id": "uuid",
      "timetable_id": "uuid",
      "class_group": "Group A",
      "planned_hours": 15,
      "delivered_hours": 12,
      "completion_rate": 80.0,
      "observations": "Good progress"
    }
  ]
}
```

#### 8. Get Course Summary
```
GET /dashboard/doyen/courses/summary/
```
Faculty-wide course summary statistics.

**Query Parameters:**
- `academic_year_id` (optional): Filter by academic year

**Response:**
```json
{
  "success": true,
  "message": "Course summary retrieved successfully",
  "data": {
    "total_courses": 45,
    "total_credits": 135,
    "courses_with_attribution": 42,
    "courses_without_attribution": 3
  }
}
```

### Additional Endpoints

#### 9. Get Courses by Class
```
GET /dashboard/doyen/courses/by-class/
```
Get all courses assigned to a specific class.

**Query Parameters:**
- `class_id` (required): Class ID
- `academic_year_id` (optional): Filter by academic year

**Response:**
```json
{
  "success": true,
  "message": "Class courses retrieved successfully",
  "data": [
    {
      "id": "uuid",
      "course_name": "Introduction to Programming",
      "course_code": "CS101",
      "credits": 3,
      "attribution_count": 2,
      "teachers": [
        {
          "id": "uuid",
          "name": "John Doe",
          "status": "Accepted"
        }
      ]
    }
  ]
}
```

#### 10. Get Courses by Teacher
```
GET /dashboard/doyen/courses/by-teacher/
```
Get all courses taught by a specific teacher.

**Query Parameters:**
- `teacher_id` (required): Teacher ID
- `academic_year_id` (optional): Filter by academic year

**Response:**
```json
{
  "success": true,
  "message": "Teacher courses retrieved successfully",
  "data": [
    {
      "id": "uuid",
      "course_name": "Introduction to Programming",
      "course_code": "CS101",
      "credits": 3,
      "attribution_id": "uuid",
      "status": "Accepted",
      "delivered_hours": 45,
      "class_name": "L1-CS"
    }
  ]
}
```

## Integration with Attribution System

The course management system deeply integrates with the attribution system:

### Attribution-Based Filtering
- Courses are filtered based on active attributions
- Attribution status affects course availability
- Substitute teachers are tracked and displayed

### Attribution Statistics
- Total attributions per course
- Status breakdown (Pending, Accepted, Refused)
- Substitute teacher assignments

### Teaching Progress Integration
- Delivered hours calculated from activity reports
- Completion rates tracked per attribution
- Teacher workload metrics

### Timetable Integration
- Timetables linked through attributions
- Activity reports provide delivery metrics
- Room utilization tracked

## Service Methods

### CourseManagementService

```python
# Get all courses for a faculty
get_faculty_courses(faculty_id, academic_year_id=None)

# Get course with all attributions
get_course_with_attributions(course_id, academic_year_id=None)

# Get comprehensive statistics
get_course_statistics(course_id, academic_year_id=None)

# Get courses by class
get_course_by_class(class_id, academic_year_id=None)

# Get courses by teacher
get_course_by_teacher(teacher_id, academic_year_id=None)

# Get enrollment statistics
get_course_enrollment(course_id, academic_year_id=None)

# Get performance metrics
get_course_performance(course_id, academic_year_id=None)

# Get timetables
get_course_timetables(course_id, academic_year_id=None)

# Get activity reports
get_course_activity_reports(course_id, academic_year_id=None)

# Get faculty summary
get_course_summary(faculty_id, academic_year_id=None)

# Get attribution status
get_course_attribution_status(course_id, academic_year_id=None)
```

## Usage Examples

### Example 1: Get Course Statistics with Attribution Details
```bash
curl -X GET "http://localhost:8000/dashboard/doyen/courses/uuid/statistics/?academic_year_id=uuid" \
  -H "Authorization: Bearer token"
```

### Example 2: Get Courses by Class
```bash
curl -X GET "http://localhost:8000/dashboard/doyen/courses/by-class/?class_id=uuid&academic_year_id=uuid" \
  -H "Authorization: Bearer token"
```

### Example 3: Get Teacher's Courses
```bash
curl -X GET "http://localhost:8000/dashboard/doyen/courses/by-teacher/?teacher_id=uuid&academic_year_id=uuid" \
  -H "Authorization: Bearer token"
```

## Permissions

All endpoints require:
- **IsDean** permission: User must be a dean
- **Faculty Scoping**: Data automatically scoped to dean's faculty
- **Academic Year**: Optional filtering by academic year

## Data Models Integration

### Course Model
- Links to Module → Class → Department → Faculty
- Has multiple Attributions
- Tracks credits and course code

### Attribution Model
- Links Course to Principal Teacher
- Supports Substitute Teachers
- Tracks status and academic year
- Links to Timetables

### Timetable Model
- Links Attribution to Class Group
- Contains Activity Reports
- Tracks delivery metrics

### ActivityReport Model
- Tracks planned vs delivered hours
- Calculates completion rates
- Provides teaching progress data

## Performance Considerations

1. **Query Optimization**
   - Uses `select_related()` for foreign keys
   - Uses `prefetch_related()` for reverse relations
   - Filters at database level

2. **Aggregation**
   - Calculates statistics efficiently
   - Uses Django ORM aggregation functions
   - Minimizes N+1 queries

3. **Caching Opportunities**
   - Course statistics can be cached
   - Faculty summaries are good cache candidates
   - Academic year filtering enables cache invalidation

## Error Handling

All endpoints return standardized responses:

**Success Response:**
```json
{
  "success": true,
  "message": "Operation successful",
  "data": {}
}
```

**Error Response:**
```json
{
  "success": false,
  "message": "Error message",
  "errors": "Detailed error information"
}
```

## Future Enhancements

1. **Course Planning**
   - Course load balancing
   - Teacher availability matching
   - Prerequisite tracking

2. **Advanced Analytics**
   - Course difficulty metrics
   - Student success prediction
   - Teacher effectiveness ratings

3. **Bulk Operations**
   - Bulk course creation
   - Batch attribution updates
   - Mass timetable generation

4. **Reporting**
   - PDF course reports
   - Excel exports
   - Custom report builder
