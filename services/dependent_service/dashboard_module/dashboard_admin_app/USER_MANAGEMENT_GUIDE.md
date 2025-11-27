# University Admin - User Management Guide

## Overview

University admins can manage all users within their university including creating users, assigning roles, changing passwords, and managing profiles.

## Features

- **Create Users**: Add new users to the university
- **Manage Users**: Update user information
- **Password Management**: Change user passwords
- **Role Assignment**: Assign roles to users
- **Profile Management**: Manage user profiles with position and dates
- **User Status**: Activate/deactivate users
- **Audit Logging**: All operations logged

## API Endpoints

### User Management

#### List Users
```
GET /api/admin/dashboard/users/
Authorization: Bearer <token>
```

Returns all users in the admin's university.

**Response:**
```json
{
  "success": true,
  "data": [
    {
      "id": "uuid",
      "email": "user@university.edu",
      "first_name": "John",
      "last_name": "Doe",
      "phone_number": "+1234567890",
      "is_active": true,
      "role": "uuid",
      "role_name": "Teacher",
      "profile": {
        "id": "uuid",
        "position": "Senior Lecturer",
        "start_date": "2024-01-01",
        "end_date": null
      },
      "created_at": "2024-01-15T10:30:00Z"
    }
  ]
}
```

#### Create User
```
POST /api/admin/dashboard/users/
Authorization: Bearer <token>
Content-Type: application/json

{
  "email": "newuser@university.edu",
  "first_name": "Jane",
  "last_name": "Smith",
  "password": "SecurePassword123!",
  "phone_number": "+1234567890",
  "role_id": "uuid"
}
```

**Response:**
```json
{
  "success": true,
  "data": {
    "id": "uuid",
    "email": "newuser@university.edu",
    "first_name": "Jane",
    "last_name": "Smith",
    "phone_number": "+1234567890",
    "is_active": true,
    "role": "uuid",
    "role_name": "Teacher"
  },
  "message": "User created successfully"
}
```

#### Get User Details
```
GET /api/admin/dashboard/users/{user_id}/
Authorization: Bearer <token>
```

#### Update User
```
PUT /api/admin/dashboard/users/{user_id}/
Authorization: Bearer <token>
Content-Type: application/json

{
  "first_name": "Jane",
  "last_name": "Smith",
  "phone_number": "+1234567890",
  "is_active": true
}
```

#### Delete User
```
DELETE /api/admin/dashboard/users/{user_id}/
Authorization: Bearer <token>
```

### Password Management

#### Change User Password
```
POST /api/admin/dashboard/users/{user_id}/password/
Authorization: Bearer <token>
Content-Type: application/json

{
  "new_password": "NewPassword123!",
  "confirm_password": "NewPassword123!"
}
```

**Response:**
```json
{
  "success": true,
  "message": "Password changed successfully"
}
```

### Role Management

#### Get Available Roles
```
GET /api/admin/dashboard/roles/
Authorization: Bearer <token>
```

**Response:**
```json
{
  "success": true,
  "data": [
    {
      "id": "uuid",
      "name": "Teacher",
      "description": "Academic staff member"
    },
    {
      "id": "uuid",
      "name": "Administrator",
      "description": "Administrative staff"
    }
  ]
}
```

#### Assign Role to User
```
POST /api/admin/dashboard/users/{user_id}/role/
Authorization: Bearer <token>
Content-Type: application/json

{
  "role_id": "uuid"
}
```

### Profile Management

#### Get User Profile
```
GET /api/admin/dashboard/users/{user_id}/profile/
Authorization: Bearer <token>
```

**Response:**
```json
{
  "success": true,
  "data": {
    "id": "uuid",
    "user_email": "user@university.edu",
    "position": "Senior Lecturer",
    "start_date": "2024-01-01",
    "end_date": null
  }
}
```

#### Update User Profile
```
PUT /api/admin/dashboard/users/{user_id}/profile/
Authorization: Bearer <token>
Content-Type: application/json

{
  "position": "Senior Lecturer",
  "start_date": "2024-01-01",
  "end_date": null
}
```

### User Status Management

#### Deactivate User
```
POST /api/admin/dashboard/users/{user_id}/deactivate/
Authorization: Bearer <token>
```

#### Activate User
```
POST /api/admin/dashboard/users/{user_id}/activate/
Authorization: Bearer <token>
```

## Usage Examples

### Python/Django

```python
from services.dependent_service.dashboard_module.dashboard_admin_app.user_management_service import UniversityUserManagementService
from services.core_service.academic_module.university_app.models import University

university = University.objects.first()

# Create user
user = UniversityUserManagementService.create_user(
    university=university,
    email="newuser@university.edu",
    first_name="John",
    last_name="Doe",
    password="SecurePassword123!",
    role_id="role-uuid"
)

# Get all users
users = UniversityUserManagementService.get_university_users(university)

# Update user
UniversityUserManagementService.update_user(
    user,
    first_name="Jane",
    phone_number="+1234567890"
)

# Change password
UniversityUserManagementService.change_user_password(user, "NewPassword123!")

# Assign role
UniversityUserManagementService.assign_role(user, "role-uuid")

# Create/update profile
profile = UniversityUserManagementService.create_user_profile(
    user,
    position="Senior Lecturer",
    start_date="2024-01-01"
)

# Deactivate user
UniversityUserManagementService.deactivate_user(user)

# Activate user
UniversityUserManagementService.activate_user(user)
```

### cURL Examples

```bash
# List users
curl -X GET http://localhost:8000/api/admin/dashboard/users/ \
  -H "Authorization: Bearer <token>"

# Create user
curl -X POST http://localhost:8000/api/admin/dashboard/users/ \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "newuser@university.edu",
    "first_name": "John",
    "last_name": "Doe",
    "password": "SecurePassword123!",
    "phone_number": "+1234567890"
  }'

# Get user details
curl -X GET http://localhost:8000/api/admin/dashboard/users/{user_id}/ \
  -H "Authorization: Bearer <token>"

# Update user
curl -X PUT http://localhost:8000/api/admin/dashboard/users/{user_id}/ \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{
    "first_name": "Jane",
    "phone_number": "+1234567890"
  }'

# Change password
curl -X POST http://localhost:8000/api/admin/dashboard/users/{user_id}/password/ \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{
    "new_password": "NewPassword123!",
    "confirm_password": "NewPassword123!"
  }'

# Get available roles
curl -X GET http://localhost:8000/api/admin/dashboard/roles/ \
  -H "Authorization: Bearer <token>"

# Assign role
curl -X POST http://localhost:8000/api/admin/dashboard/users/{user_id}/role/ \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{"role_id": "role-uuid"}'

# Get user profile
curl -X GET http://localhost:8000/api/admin/dashboard/users/{user_id}/profile/ \
  -H "Authorization: Bearer <token>"

# Update user profile
curl -X PUT http://localhost:8000/api/admin/dashboard/users/{user_id}/profile/ \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{
    "position": "Senior Lecturer",
    "start_date": "2024-01-01"
  }'

# Deactivate user
curl -X POST http://localhost:8000/api/admin/dashboard/users/{user_id}/deactivate/ \
  -H "Authorization: Bearer <token>"

# Activate user
curl -X POST http://localhost:8000/api/admin/dashboard/users/{user_id}/activate/ \
  -H "Authorization: Bearer <token>"
```

## Access Control

- University admins can only manage users in their university
- All operations require authentication
- Automatic university scoping via admin profile
- Audit logging on all operations

## Security Features

- Password hashing using Django's default algorithm
- Password validation (minimum 8 characters)
- Audit trail of all user operations
- User status management (active/inactive)
- Role-based access control

## Models Used

### User (from user_app)
- Email, first_name, last_name
- Phone number, birth date, gender
- University reference
- Role assignment
- Active status

### Profile (from authorization_app)
- Position
- Start date, end date
- Room assignment
- Faculty/University context

### Role (from user_app)
- Name, description
- Used for role-based access control

## Audit Logging

All user management operations are logged with:
- User who performed action
- Action type (create, update, delete)
- User affected
- Changes made
- Timestamp
- Success/failure status

## Best Practices

1. **Password Security**: Use strong passwords (min 8 characters)
2. **Role Assignment**: Assign appropriate roles based on responsibilities
3. **Profile Completion**: Fill in position and dates for better tracking
4. **Regular Audits**: Review audit logs for suspicious activities
5. **User Status**: Deactivate users who leave the university
6. **Profile Updates**: Keep user profiles current

## Troubleshooting

### User Creation Failed

Check:
- Email is unique
- Password meets requirements (min 8 characters)
- University is set correctly
- Role ID is valid (if provided)

### Password Change Failed

Check:
- Passwords match
- Password meets requirements
- User exists and belongs to university

### Role Assignment Failed

Check:
- Role ID is valid
- Role exists in system
- User exists and belongs to university

## Limitations

- Admins can only manage users in their university
- Cannot modify superuser accounts
- Cannot change user's university
- Email must be unique across system
