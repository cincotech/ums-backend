# Filter Implementation Guide - UMS Backend

## Overview
All ViewSets across the UMS Backend now support:
- **Filterset Classes**: Custom filter classes based on serializer fields
- **Q-based Search**: Multi-field search using Django Q objects
- **Pagination**: Automatic pagination via BaseViewSet
- **Ordering**: Sort by specified fields

## Pattern Used

### 1. Filter File Structure (filters.py)
```python
import django_filters
from django.db.models import Q
from .models import ModelName


class ModelNameFilter(django_filters.FilterSet):
    # Exact filters (UUID, Boolean, Date, etc.)
    field_name = django_filters.UUIDFilter(field_name='field_name')

    # Search filters (icontains for individual fields)
    field_name = django_filters.CharFilter(field_name='field_name', lookup_expr='icontains')

    # Q-based multi-field search
    search = django_filters.CharFilter(method='filter_search')

    class Meta:
        model = ModelName
        fields = ['exact_filter_fields']

    def filter_search(self, queryset, name, value):
        return queryset.filter(
            Q(field1__icontains=value) |
            Q(field2__icontains=value) |
            Q(related__field__icontains=value)
        )
```

### 2. ViewSet Configuration
```python
from .filters import ModelNameFilter

class ModelNameViewSet(BaseViewSet):
    queryset = ModelName.objects.all()
    serializer_class = ModelNameSerializer
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_class = ModelNameFilter  # Use filterset_class instead of filterset_fields
    search_fields = ['field1', 'field2']  # For DRF SearchFilter (optional)
    ordering_fields = ['field1', 'field2']
    ordering = ['-created_at']
```

## Apps with Filter Implementation

### Core Service - Student Module
1. **inscription_app** ✅
   - InscriptionFilter with academic year filtering
   - Search: student name, matricule, class name, status

2. **student_profile_app** ✅
   - StudentFilter
   - Search: first name, last name, email, matricule

3. **card_app** ✅
   - CardFilter
   - Search: student matricule, card number, status

4. **parent_app** ✅
   - ParentFilter
   - Search: student matricule, parent name, phone

### Core Service - Academic Module
1. **class_app** ✅
   - ClassFilter
   - Search: class name, code, department name

2. **department_app** ✅
   - DepartmentFilter
   - Search: department name, code, faculty name

3. **faculty_app** ✅
   - FacultyFilter
   - Search: faculty name, code

4. **course_app** ✅
   - CourseFilter
   - Search: course name, code, teacher name

5. **module_app** ✅
   - ModuleFilter
   - Search: module name, code

6. **teacher_app** ✅
   - TeacherFilter
   - Search: first name, last name, email, speciality

7. **university_app** ✅
   - UniversityFilter, AcademicYearFilter, UniversityDegreeFilter
   - Search: university name, code

### Foundational Service - Auth Module
1. **authentication_app** ✅
   - UserFilter
   - Search: email, first name, last name, phone

2. **guest_app** ✅
   - GuestRequestFilter
   - Search: user email, name, status

## API Usage Examples

### 1. Q-based Multi-field Search
```
GET /api/students/?search=john
```
Searches across: first_name, last_name, email, matricule

### 2. Individual Field Filtering
```
GET /api/inscriptions/?student_first_name=john&regist_status=Active
```

### 3. Exact Filtering
```
GET /api/inscriptions/?student=uuid&academic_year=uuid
```

### 4. Date Range Filtering
```
GET /api/inscriptions/?date_inscription__gte=2024-01-01&date_inscription__lte=2024-12-31
```

### 5. Pagination
```
GET /api/students/?page=1&page_size=20
```

### 6. Ordering
```
GET /api/students/?ordering=-created_at
GET /api/students/?ordering=matricule
```

### 7. Combined Filters
```
GET /api/inscriptions/?search=john&regist_status=Active&ordering=-date_inscription&page=1
```

## Benefits for Frontend

1. **Clear API Contract**: Frontend knows exactly which fields are filterable
2. **Type Safety**: Filters match serializer field types
3. **Flexible Search**: Single `search` parameter for quick searches
4. **Granular Control**: Individual field filters for advanced filtering
5. **Consistent Pattern**: Same pattern across all endpoints

## Adding Filters to New Apps

1. Create `filters.py` in the app directory
2. Define filter class based on serializer fields
3. Add `search` filter with Q objects for multi-field search
4. Import filter class in `views.py`
5. Set `filterset_class = YourFilter` in ViewSet
6. Ensure `filter_backends` includes `DjangoFilterBackend`

## Notes

- All filters use `icontains` for case-insensitive partial matching
- Q-based search combines multiple fields with OR logic
- BaseViewSet handles pagination automatically
- Use `?pagination=false` to disable pagination
- Filters work seamlessly with BaseViewSet's list method
