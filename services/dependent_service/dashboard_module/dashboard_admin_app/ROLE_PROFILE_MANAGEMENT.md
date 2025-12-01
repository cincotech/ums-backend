# Role-Specific Profile Management

## Overview

University admins can create and manage users with role-specific profiles. Each role has unique profile fields based on their position in the university hierarchy.

## Supported Roles & Profiles

### 1. Rector
- **Profile Fields**: University, Position, Room, Start Date, End Date
- **Description**: University rector/president

### 2. Dean
- **Profile Fields**: Faculty, Position, Room, Start Date, End Date
- **Description**: Faculty dean

### 3. Student Service
- **Profile Fields**: Position, Room, Start Date, End Date
- **Description**: Student services staff

### 4. Finance Service
- **Profile Fields**: Position, Room, Start Date, End Date
- **Description**: Finance department staff

### 5. General Service
- **Profile Fields**: Position, Room, Start Date, End Date
- **Description**: General administrative staff

### 6. Rector Office
- **Profile Fields**: Position, Room, Start Date, End Date
- **Description**: Rector's office staff

### 7. Quality Insurance
- **Profile Fields**: Position, Room, Start Date, End Date
- **Description**: Quality assurance staff

### 8. Academic Affairs
- **Profile Fields**: Position, Room, Start Date, End Date
- **Description**: Academic affairs staff

## API Endpoints

### Get Role Information

#### Get All Roles with Required Fields
```
GET /api/admin/dashboard/roles/fields/
Authorization: Bearer <token>
```

**Response:**
```json
{
  "success": true,
  "data": [
    {
      "id": "uuid",
      "name": "Rector",
      "description": "University rector/president",
      "fields": {
        "position": "string",
        "start_date": "date",
        "end_date": "date (optional)",
        "room_id": "uuid (optional)",
        "university_id": "uuid (required)"
      }
    },
    {
      "id": "uuid",
      "name": "Dean",
      "description": "Faculty dean",
      "fields": {
        "position": "string",
        "start_date": "date",
        "end_date": "date (optional)",
        "room_id": "uuid (optional)",
        "faculty_id": "uuid (required)"
      }
    }
  ]
}
```

### Create User with Profile

#### Create User with Role-Specific Profile
```
POST /api/admin/dashboard/users/create-with-profile/
Authorization: Bearer <token>
Content-Type: application/json
```

**For Rector:**
```json
{
  "email": "rector@university.edu",
  "first_name": "John",
  "last_name": "Doe",
  "password": "SecurePassword123!",
  "role_name": "Rector",
  "position": "Rector",
  "start_date": "2024-01-01",
  "end_date": null,
  "room_id": "room-uuid",
  "university_id": "university-uuid"
}
```

**For Dean:**
```json
{
  "email": "dean@university.edu",
  "first_name": "Jane",
  "last_name": "Smith",
  "password": "SecurePassword123!",
  "role_name": "Dean",
  "position": "Dean of Faculty",
  "start_date": "2024-01-01",
  "end_date": null,
  "room_id": "room-uuid",
  "faculty_id": "faculty-uuid"
}
```

**For Other Roles:**
```json
{
  "email": "staff@university.edu",
  "first_name": "Bob",
  "last_name": "Johnson",
  "password": "SecurePassword123!",
  "role_name": "Student Service",
  "position": "Student Services Manager",
  "start_date": "2024-01-01",
  "end_date": null,
  "room_id": "room-uuid"
}
```

**Response:**
```json
{
  "success": true,
  "data": {
    "user_id": "uuid",
    "email": "rector@university.edu",
    "first_name": "John",
    "last_name": "Doe",
    "role": "Rector",
    "profile": {
      "id": "uuid",
      "position": "Rector",
      "start_date": "2024-01-01",
      "end_date": null,
      "room": "room-uuid",
      "university": "university-uuid"
    }
  },
  "message": "User with profile created successfully"
}
```

### Get User Profile

#### Get User Profile with Role-Specific Data
```
GET /api/admin/dashboard/users/{user_id}/profile-detail/
Authorization: Bearer <token>
```

**Response:**
```json
{
  "success": true,
  "data": {
    "user_id": "uuid",
    "email": "rector@university.edu",
    "first_name": "John",
    "last_name": "Doe",
    "role": "Rector",
    "profile": {
      "id": "uuid",
      "position": "Rector",
      "start_date": "2024-01-01",
      "end_date": null,
      "room": "room-uuid",
      "room_name": "Room 101",
      "university": "university-uuid",
      "university_name": "University Name"
    }
  }
}
```

### Update User Profile

#### Update User Profile with Role-Specific Data
```
PUT /api/admin/dashboard/users/{user_id}/profile-update/
Authorization: Bearer <token>
Content-Type: application/json
```

**For Rector:**
```json
{
  "position": "Rector",
  "start_date": "2024-01-01",
  "end_date": "2026-12-31",
  "room_id": "room-uuid",
  "university_id": "university-uuid"
}
```

**For Dean:**
```json
{
  "position": "Dean of Faculty",
  "start_date": "2024-01-01",
  "end_date": "2026-12-31",
  "room_id": "room-uuid",
  "faculty_id": "faculty-uuid"
}
```

## Usage Examples

### Python/Django

```python
from services.dependent_service.dashboard_module.dashboard_admin_app.role_profile_service import RoleProfileService
from services.core_service.academic_module.university_app.models import University

university = University.objects.first()

# Get all roles with fields
roles = RoleProfileService.get_all_roles_with_fields()
for role in roles:
    print(f"{role['name']}: {role['fields']}")

# Create rector with profile
rector = RoleProfileService.create_user_with_profile(
    university=university,
    email="rector@university.edu",
    first_name="John",
    last_name="Doe",
    password="SecurePassword123!",
    role_name="Rector",
    profile_data={
        "position": "Rector",
        "start_date": "2024-01-01",
        "university_id": "university-uuid"
    }
)

# Create dean with profile
dean = RoleProfileService.create_user_with_profile(
    university=university,
    email="dean@university.edu",
    first_name="Jane",
    last_name": "Smith",
    password="SecurePassword123!",
    role_name="Dean",
    profile_data={
        "position": "Dean of Faculty",
        "start_date": "2024-01-01",
        "faculty_id": "faculty-uuid"
    }
)

# Get user profile data
profile_data = RoleProfileService.get_user_profile_data(rector)
print(profile_data)

# Update user profile
updated_profile = RoleProfileService.update_user_profile(
    rector,
    "Rector",
    {
        "position": "Rector",
        "start_date": "2024-01-01",
        "end_date": "2026-12-31",
        "university_id": "university-uuid"
    }
)
```

### cURL Examples

```bash
# Get all roles with fields
curl -X GET http://localhost:8000/api/admin/dashboard/roles/fields/ \
  -H "Authorization: Bearer <token>"

# Create rector with profile
curl -X POST http://localhost:8000/api/admin/dashboard/users/create-with-profile/ \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "rector@university.edu",
    "first_name": "John",
    "last_name": "Doe",
    "password": "SecurePassword123!",
    "role_name": "Rector",
    "position": "Rector",
    "start_date": "2024-01-01",
    "university_id": "university-uuid"
  }'

# Create dean with profile
curl -X POST http://localhost:8000/api/admin/dashboard/users/create-with-profile/ \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "dean@university.edu",
    "first_name": "Jane",
    "last_name": "Smith",
    "password": "SecurePassword123!",
    "role_name": "Dean",
    "position": "Dean of Faculty",
    "start_date": "2024-01-01",
    "faculty_id": "faculty-uuid"
  }'

# Get user profile
curl -X GET http://localhost:8000/api/admin/dashboard/users/{user_id}/profile-detail/ \
  -H "Authorization: Bearer <token>"

# Update user profile
curl -X PUT http://localhost:8000/api/admin/dashboard/users/{user_id}/profile-update/ \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{
    "position": "Rector",
    "start_date": "2024-01-01",
    "end_date": "2026-12-31",
    "university_id": "university-uuid"
  }'
```

## Profile Model Structure

The Profile model inherits from multiple role-specific base classes:

```
Profile
├── BaseProfile (common fields)
│   ├── position
│   ├── room
│   ├── start_date
│   └── end_date
├── Rector
│   └── university
├── Dean
│   └── faculty
├── StudentService
├── FinanceService
├── GeneralService
├── RectorOffice
├── QualityInsurance
└── AcademicAffairs
```

## Field Validation

- **position**: Required, max 100 characters
- **start_date**: Required, date format (YYYY-MM-DD)
- **end_date**: Optional, date format (YYYY-MM-DD)
- **room_id**: Optional, must exist in Room model
- **university_id**: Required for Rector role, must exist in University model
- **faculty_id**: Required for Dean role, must exist in Faculty model

## Access Control

- University admins can only create/manage users in their university
- All operations require authentication
- Automatic university scoping
- Full audit logging

## Best Practices

1. **Role Selection**: Choose correct role based on position
2. **Profile Completion**: Fill all required fields for the role
3. **Date Management**: Set appropriate start and end dates
4. **Room Assignment**: Assign office/room when available
5. **Audit Review**: Monitor audit logs for user management activities

## Error Handling

Common errors and solutions:

| Error | Cause | Solution |
|-------|-------|----------|
| "User with email already exists" | Email not unique | Use different email |
| "Room not found" | Invalid room_id | Verify room exists |
| "University not found" | Invalid university_id | Verify university exists |
| "Faculty not found" | Invalid faculty_id | Verify faculty exists |
| "Validation error" | Missing required fields | Check role requirements |

## Limitations

- Admins can only manage users in their university
- Cannot modify superuser accounts
- Email must be unique across system
- Role-specific fields are validated based on role
