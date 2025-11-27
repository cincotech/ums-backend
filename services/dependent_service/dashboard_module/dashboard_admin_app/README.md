# University Admin Dashboard

The University Admin Dashboard provides university administrators with comprehensive management tools for their institution. Each admin manages exactly one university with full control over configurations, statistics, and notifications.

## Features

- **Dashboard Overview**: Real-time statistics and metrics for the university
- **Configuration Management**: Manage university-specific settings across multiple categories
- **Statistics Tracking**: Comprehensive academic and operational metrics
- **Notifications**: System notifications for admins with priority levels
- **Audit Logging**: Complete audit trail of all admin activities

## API Endpoints

### Dashboard

#### Get Dashboard Overview
```
GET /api/admin/dashboard/overview/
```

Returns comprehensive dashboard statistics including:
- Total students, teachers, faculties, departments, courses
- Active enrollments and completed exams
- Pending document requests
- Pending notifications count
- Recent activities count

**Response:**
```json
{
  "success": true,
  "data": {
    "id": "uuid",
    "university": "uuid",
    "university_name": "University Name",
    "total_students": 1500,
    "total_teachers": 150,
    "total_faculties": 5,
    "total_departments": 20,
    "total_courses": 200,
    "active_enrollments": 1200,
    "completed_exams": 450,
    "pending_document_requests": 25,
    "pending_notifications": 5,
    "recent_activities": 42,
    "calculated_at": "2024-01-15T10:30:00Z"
  }
}
```

### Configuration Management

#### List All Configurations
```
GET /api/admin/dashboard/configurations/
```

Optional query parameters:
- `category`: Filter by category (academic, financial, enrollment, notification, security, feature, general)

**Response:**
```json
{
  "success": true,
  "data": [
    {
      "id": "uuid",
      "university": "uuid",
      "category": "academic",
      "key": "semester_duration",
      "value": {"weeks": 16},
      "description": "Duration of academic semester",
      "is_active": true,
      "created_by_email": "admin@university.edu",
      "created_at": "2024-01-01T00:00:00Z",
      "updated_at": "2024-01-15T10:30:00Z"
    }
  ]
}
```

#### Create Configuration
```
POST /api/admin/dashboard/configurations/
Content-Type: application/json

{
  "category": "academic",
  "key": "semester_duration",
  "value": {"weeks": 16},
  "description": "Duration of academic semester",
  "is_active": true
}
```

#### Get Configuration Detail
```
GET /api/admin/dashboard/configurations/{config_id}/
```

#### Update Configuration
```
PUT /api/admin/dashboard/configurations/{config_id}/
Content-Type: application/json

{
  "value": {"weeks": 17},
  "is_active": true
}
```

#### Delete Configuration
```
DELETE /api/admin/dashboard/configurations/{config_id}/
```

### Statistics

#### Get University Statistics
```
GET /api/admin/dashboard/statistics/
```

Returns detailed statistics for the university including all academic and operational metrics.

### Notifications

#### List Notifications
```
GET /api/admin/dashboard/notifications/
```

Returns up to 50 most recent notifications for the admin.

#### Mark Notification as Read
```
POST /api/admin/dashboard/notifications/{notification_id}/read/
```

### Audit Logs

#### Get Audit Logs
```
GET /api/admin/dashboard/audit-logs/
```

Optional query parameters:
- `days`: Number of days to look back (default: 7)

Returns up to 100 audit log entries for the university.

## Service Classes

### UniversityAdminService

Handles dashboard operations for a single university.

**Methods:**
- `get_dashboard_stats(university)`: Get comprehensive statistics
- `update_university_statistics(university)`: Update or create statistics record
- `create_notification(university, recipient, title, message, ...)`: Create notification

### ConfigurationService

Manages university configurations.

**Methods:**
- `get_or_create_config(university, category, key, default_value)`: Get or create config
- `update_config(university, category, key, value, modified_by)`: Update config value
- `get_category_configs(university, category)`: Get all configs for category
- `get_all_configs(university)`: Get all active configurations

## Usage Examples

### Python/Django

```python
from services.dependent_service.dashboard_module.dashboard_admin_app.services import (
    UniversityAdminService,
    ConfigurationService
)

# Get dashboard statistics
stats = UniversityAdminService.get_dashboard_stats(university)

# Update statistics
updated_stats = UniversityAdminService.update_university_statistics(university)

# Create notification
notification = UniversityAdminService.create_notification(
    university=university,
    recipient=admin_user,
    title="System Update",
    message="System maintenance scheduled",
    notification_type="warning",
    priority="high"
)

# Get or create configuration
config = ConfigurationService.get_or_create_config(
    university=university,
    category="academic",
    key="semester_duration",
    default_value={"weeks": 16}
)

# Update configuration
updated_config = ConfigurationService.update_config(
    university=university,
    category="academic",
    key="semester_duration",
    value={"weeks": 17},
    modified_by=admin_user
)

# Get all configurations for a category
academic_configs = ConfigurationService.get_category_configs(
    university=university,
    category="academic"
)
```

### cURL Examples

```bash
# Get dashboard overview
curl -X GET http://localhost:8000/api/admin/dashboard/overview/ \
  -H "Authorization: Bearer <token>"

# List configurations
curl -X GET http://localhost:8000/api/admin/dashboard/configurations/ \
  -H "Authorization: Bearer <token>"

# Create configuration
curl -X POST http://localhost:8000/api/admin/dashboard/configurations/ \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{
    "category": "academic",
    "key": "semester_duration",
    "value": {"weeks": 16},
    "description": "Duration of academic semester"
  }'

# Get statistics
curl -X GET http://localhost:8000/api/admin/dashboard/statistics/ \
  -H "Authorization: Bearer <token>"

# Get audit logs (last 30 days)
curl -X GET "http://localhost:8000/api/admin/dashboard/audit-logs/?days=30" \
  -H "Authorization: Bearer <token>"
```

## Access Control

All endpoints require:
1. User authentication (IsAuthenticated)
2. Active university admin profile
3. Access is automatically scoped to the admin's university

The system automatically extracts the university from `request.user.university_admin_profile.university` and ensures all operations are scoped to that university.

## Audit Logging

All operations are automatically logged with:
- Action type (create, update, delete, view)
- Entity type and ID
- Changes (old/new values)
- Request context (IP address, user agent)
- Timestamp and user information

## Error Handling

All endpoints return consistent error responses:

```json
{
  "success": false,
  "message": "Error description",
  "errors": {},
  "status_code": 400
}
```

Common status codes:
- `200`: Success
- `201`: Created
- `400`: Validation error
- `403`: Permission denied
- `404`: Not found
- `500`: Server error

## Configuration Categories

- **academic**: Academic settings (semester duration, grading scales, etc.)
- **financial**: Financial settings (fees, payment terms, etc.)
- **enrollment**: Enrollment settings (capacity, deadlines, etc.)
- **notification**: Notification settings (email templates, schedules, etc.)
- **security**: Security settings (password policies, 2FA, etc.)
- **feature**: Feature flags (enable/disable features)
- **general**: General settings (university info, contact details, etc.)

## Notification Types

- **system**: System notifications
- **alert**: Alerts requiring attention
- **warning**: Warning messages
- **info**: Informational messages
- **success**: Success confirmations

## Priority Levels

- **low**: Low priority
- **medium**: Medium priority
- **high**: High priority
- **critical**: Critical priority
