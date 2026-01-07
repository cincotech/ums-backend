# Course Management System - Quick Reference Guide

## File Structure

```
dashboard_doyen_app/
├── course_management_service.py      # Business logic
├── course_management_serializers.py  # Data validation
├── course_management_views.py        # API endpoints
├── urls.py                           # URL routing (updated)
├── COURSE_MANAGEMENT.md              # Full documentation
└── views.py                          # Existing views
```

## Quick Start

### 1. Get All Courses for Faculty
```python
from course_management_service import CourseManagementService

courses = CourseManagementService.get_faculty_courses(
    faculty_id='uuid',
    academic_year_id='uuid'  # optional
)
```

### 2. Get Course Statistics
```python
stats = CourseManagementService.get_course_statistics(
    course_id='uuid',
    academic_year_id='uuid'  # optional
)
# Returns: {
#   'course_id', 'course_name', 'course_code', 'credits',
#   'total_attributions', 'accepted_attributions', 'pending_attributions',
#   'total_timetables', 'published_timetables',
#   'total_planned_hours', 'total_delivered_hours', 'avg_completion_rate',
#   'total_students'
# }
```

### 3. Get Courses by Class
```python
courses = CourseManagementService.get_course_by_class(
    class_id='uuid',
    academic_year_id='uuid'  # optional
)
# Returns: [
#   {
#     'id', 'course_name', 'course_code', 'credits',
#     'attribution_count', 'teachers': [{'id', 'name', 'status'}]
#   }
# ]
```

### 4. Get Courses by Teacher
```python
courses = CourseManagementService.get_course_by_teacher(
    teacher_id='uuid',
    academic_year_id='uuid'  # optional
)
# Returns: [
#   {
#     'id', 'course_name', 'course_code', 'credits',
#     'attribution_id', 'status', 'delivered_hours', 'class_name'
#   }
# ]
```

### 5. Get Course Enrollment
```python
enrollment = CourseManagementService.get_course_enrollment(
    course_id='uuid',
    academic_year_id='uuid'  # optional
)
# Returns: {
#   'course_id', 'course_name', 'total_enrolled',
#   'male', 'female', 'by_class': [...]
# }
```

### 6. Get Course Performance
```python
performance = CourseManagementService.get_course_performance(
    course_id='uuid',
    academic_year_id='uuid'  # optional
)
# Returns: {
#   'course_id', 'course_name', 'total_results',
#   'average_mark', 'pass_rate', 'fail_rate'
# }
```

### 7. Get Attribution Status
```python
status = CourseManagementService.get_course_attribution_status(
    course_id='uuid',
    academic_year_id='uuid'  # optional
)
# Returns: {
#   'course_id', 'total_attributions',
#   'status_breakdown': {'pending', 'accepted', 'refused', 'with_substitute'},
#   'attributions': [...]
# }
```

## API Endpoints Quick Reference

| Method | Endpoint | Purpose |
|--------|----------|---------|
| GET | `/courses/` | List all courses |
| GET | `/courses/by_faculty/` | Get faculty courses |
| GET | `/courses/{id}/` | Get course details |
| GET | `/courses/{id}/statistics/` | Get course statistics |
| GET | `/courses/{id}/enrollment/` | Get enrollment data |
| GET | `/courses/{id}/performance/` | Get performance metrics |
| GET | `/courses/{id}/attributions/` | Get attribution status |
| GET | `/courses/{id}/activity_reports/` | Get activity reports |
| GET | `/courses/summary/` | Get faculty summary |
| GET | `/courses/by-class/` | Get courses by class |
| GET | `/courses/by-teacher/` | Get courses by teacher |

## Query Parameters

### Academic Year Filtering
```
?academic_year_id=uuid
```

### Class Filtering
```
?class_id=uuid
```

### Teacher Filtering
```
?teacher_id=uuid
```

### Combined
```
?class_id=uuid&academic_year_id=uuid
```

## Response Format

### Success Response
```json
{
  "success": true,
  "message": "Operation successful",
  "data": {
    // Response data
  }
}
```

### Error Response
```json
{
  "success": false,
  "message": "Error message",
  "errors": "Detailed error information"
}
```

## Common Use Cases

### Use Case 1: Dean Views Course Dashboard
```bash
# Get all courses
GET /courses/by_faculty/?academic_year_id=uuid

# Get course statistics
GET /courses/{id}/statistics/?academic_year_id=uuid

# Get enrollment
GET /courses/{id}/enrollment/?academic_year_id=uuid

# Get performance
GET /courses/{id}/performance/?academic_year_id=uuid
```

### Use Case 2: Dean Checks Class Courses
```bash
# Get all courses for a class
GET /courses/by-class/?class_id=uuid&academic_year_id=uuid

# For each course, get statistics
GET /courses/{id}/statistics/?academic_year_id=uuid
```

### Use Case 3: Dean Reviews Teacher Workload
```bash
# Get all courses taught by teacher
GET /courses/by-teacher/?teacher_id=uuid&academic_year_id=uuid

# Get attribution status
GET /courses/{id}/attributions/?academic_year_id=uuid
```

### Use Case 4: Dean Monitors Teaching Progress
```bash
# Get course activity reports
GET /courses/{id}/activity_reports/?academic_year_id=uuid

# Get course statistics (includes completion rate)
GET /courses/{id}/statistics/?academic_year_id=uuid
```

## Integration with Attribution System

### Key Integration Points

1. **Attribution Status**
   - Pending: Course not yet confirmed by teacher
   - Accepted: Course confirmed by teacher
   - Refused: Course refused by teacher

2. **Substitute Teachers**
   - Tracked in attribution
   - Displayed in course details
   - Counted in attribution statistics

3. **Teaching Progress**
   - Linked through attribution to timetable
   - Activity reports track delivery
   - Completion rates calculated

### Example: Get Course with Full Attribution Details
```python
course_data = CourseManagementService.get_course_with_attributions(
    course_id='uuid',
    academic_year_id='uuid'
)

# Access attribution details
for attr in course_data['attributions']:
    print(f"Teacher: {attr.principal_teacher.user.first_name}")
    print(f"Status: {attr.status_principal_teacher}")
    print(f"Substitute: {attr.substitute_teacher}")
```

## Filtering & Sorting

### Filtering by Status
```python
# In service method
attributions = Attribution.objects.filter(
    course=course,
    status_principal_teacher='Accepted'
)
```

### Sorting by Completion Rate
```python
# Activity reports sorted by completion rate
reports = ActivityReport.objects.filter(
    timetable__attribution__course=course
).order_by('-completion_rate')
```

## Performance Tips

1. **Use Academic Year Filtering**
   - Reduces query scope
   - Improves response time
   - Enables caching

2. **Batch Requests**
   - Get multiple courses at once
   - Reduces API calls
   - Better performance

3. **Cache Results**
   - Statistics can be cached
   - Invalidate on attribution changes
   - Reduces database load

## Troubleshooting

### Issue: No courses returned
**Solution:** Check if user is dean and has faculty assigned
```python
user.profiles.faculty  # Should not be None
```

### Issue: Attribution status not showing
**Solution:** Ensure academic year is specified
```python
?academic_year_id=uuid
```

### Issue: Slow performance
**Solution:** Check query optimization
- Use select_related for foreign keys
- Use prefetch_related for reverse relations
- Add academic year filter

### Issue: Enrollment numbers don't match
**Solution:** Check inscription status
- Only counts 'Active' inscriptions
- Excludes withdrawn students
- Filters by academic year

## Common Errors

| Error | Cause | Solution |
|-------|-------|----------|
| 404 Not Found | Course doesn't exist | Verify course ID |
| 403 Forbidden | Not a dean | Check user role |
| 400 Bad Request | Missing required param | Add class_id or teacher_id |
| 500 Server Error | Database error | Check database connection |

## Testing Examples

### Test Get Faculty Courses
```python
def test_get_faculty_courses():
    courses = CourseManagementService.get_faculty_courses(
        faculty_id=faculty.id,
        academic_year_id=academic_year.id
    )
    assert len(courses) > 0
    assert courses[0].course_name is not None
```

### Test Get Course Statistics
```python
def test_get_course_statistics():
    stats = CourseManagementService.get_course_statistics(
        course_id=course.id,
        academic_year_id=academic_year.id
    )
    assert stats['total_attributions'] >= 0
    assert stats['total_students'] >= 0
```

### Test Get Courses by Class
```python
def test_get_course_by_class():
    courses = CourseManagementService.get_course_by_class(
        class_id=class_obj.id,
        academic_year_id=academic_year.id
    )
    assert len(courses) > 0
    assert courses[0]['class_name'] == class_obj.class_name
```

## Useful Django ORM Patterns

### Get courses with attribution count
```python
from django.db.models import Count

courses = Course.objects.annotate(
    attribution_count=Count('attribution')
).filter(attribution_count__gt=0)
```

### Get average completion rate
```python
from django.db.models import Avg

avg_rate = ActivityReport.objects.filter(
    timetable__attribution__course=course
).aggregate(avg=Avg('completion_rate'))['avg']
```

### Get enrollment by gender
```python
from django.db.models import Count

by_gender = Inscription.objects.filter(
    class_fk__module__course=course
).values('student__user__gender').annotate(count=Count('id'))
```

## Related Documentation

- **COURSE_MANAGEMENT.md** - Full API documentation
- **COURSE_MANAGEMENT_ARCHITECTURE.md** - System architecture
- **services.py** - Other dashboard services
- **views.py** - Other dashboard views

## Support & Maintenance

### Adding New Endpoint
1. Add method to CourseManagementService
2. Create serializer in course_management_serializers.py
3. Add action to CourseViewSet or create new view
4. Register in urls.py
5. Update documentation

### Modifying Existing Endpoint
1. Update service method
2. Update serializer if needed
3. Test with different academic years
4. Update documentation

### Performance Optimization
1. Profile queries with Django Debug Toolbar
2. Add select_related/prefetch_related
3. Use aggregation at DB level
4. Implement caching if needed
