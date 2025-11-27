# University Subscription Management Guide

## Overview

Super admins can manage university profiles and subscriptions to system modules. Each university can subscribe to different modules with specific time periods.

## Features

- **University Profiles**: Manage university metadata and settings
- **Module Management**: System modules available for subscription
- **Subscriptions**: Subscribe universities to modules with time periods
- **Renewal**: Renew expiring subscriptions
- **Expiry Tracking**: Monitor subscriptions expiring soon
- **Audit Logging**: All operations logged

## Models

### UniversityProfile
- University reference
- Status (active, inactive, suspended, trial)
- Contact information
- Website, logo, description
- Resource limits (max users, storage)

### Module
- Name, description, code
- Active status
- System modules available for subscription

### UniversitySubscription
- University reference
- Module reference
- Status (active, inactive, expired, suspended)
- Start and end dates
- Trial flag
- Audit trail

## API Endpoints

### University Profile

#### Get University Profile
```
GET /api/super-admin/universities/{university_id}/profile/
Authorization: Bearer <token>
```

**Response:**
```json
{
  "success": true,
  "data": {
    "id": "uuid",
    "university": "uuid",
    "university_name": "University Name",
    "status": "active",
    "contact_email": "admin@university.edu",
    "contact_phone": "+1234567890",
    "website": "https://university.edu",
    "description": "University description",
    "max_users": 1000,
    "max_storage_gb": 100,
    "created_at": "2024-01-01T00:00:00Z",
    "updated_at": "2024-01-15T10:30:00Z"
  }
}
```

#### Update University Profile
```
PUT /api/super-admin/universities/{university_id}/profile/
Authorization: Bearer <token>
Content-Type: application/json

{
  "status": "active",
  "contact_email": "admin@university.edu",
  "contact_phone": "+1234567890",
  "website": "https://university.edu",
  "description": "Updated description",
  "max_users": 1500,
  "max_storage_gb": 150
}
```

### Modules

#### Get All Modules
```
GET /api/super-admin/modules/
Authorization: Bearer <token>
```

**Response:**
```json
{
  "success": true,
  "data": [
    {
      "id": "uuid",
      "name": "Academic Management",
      "description": "Module for academic operations",
      "code": "academic",
      "is_active": true,
      "created_at": "2024-01-01T00:00:00Z"
    },
    {
      "id": "uuid",
      "name": "Student Management",
      "description": "Module for student operations",
      "code": "student",
      "is_active": true,
      "created_at": "2024-01-01T00:00:00Z"
    }
  ]
}
```

### Subscriptions

#### Get University Subscriptions
```
GET /api/super-admin/universities/{university_id}/subscriptions/
Authorization: Bearer <token>
```

**Response:**
```json
{
  "success": true,
  "data": [
    {
      "id": "uuid",
      "university": "uuid",
      "university_name": "University Name",
      "module": "uuid",
      "module_name": "Academic Management",
      "module_code": "academic",
      "status": "active",
      "start_date": "2024-01-01",
      "end_date": "2024-12-31",
      "is_trial": false,
      "created_by_email": "admin@system.edu",
      "days_remaining": 320,
      "is_expired": false,
      "created_at": "2024-01-01T00:00:00Z",
      "updated_at": "2024-01-15T10:30:00Z"
    }
  ]
}
```

#### Create Subscription
```
POST /api/super-admin/universities/{university_id}/subscriptions/
Authorization: Bearer <token>
Content-Type: application/json

{
  "module_id": "uuid",
  "start_date": "2024-01-01",
  "end_date": "2024-12-31",
  "is_trial": false
}
```

#### Cancel Subscription
```
POST /api/super-admin/subscriptions/{subscription_id}/cancel/
Authorization: Bearer <token>
```

#### Renew Subscription
```
POST /api/super-admin/subscriptions/{subscription_id}/renew/
Authorization: Bearer <token>
Content-Type: application/json

{
  "new_end_date": "2025-12-31"
}
```

#### Get Expiring Subscriptions
```
GET /api/super-admin/subscriptions/expiring/?days=30
Authorization: Bearer <token>
```

Returns subscriptions expiring within specified days.

## Usage Examples

### Python/Django

```python
from services.dependent_service.dashboard_module.dashboard_super_admin_app.subscription_service import (
    UniversityProfileService,
    ModuleService,
    SubscriptionService
)
from services.core_service.academic_module.university_app.models import University
from django.contrib.auth import get_user_model

User = get_user_model()
university = University.objects.first()
admin_user = User.objects.filter(is_superuser=True).first()

# Create university profile
profile = UniversityProfileService.create_profile(
    university=university,
    contact_email="admin@university.edu",
    contact_phone="+1234567890",
    website="https://university.edu"
)

# Update profile
UniversityProfileService.update_profile(
    university,
    status="active",
    max_users=1500,
    max_storage_gb=150
)

# Get all modules
modules = ModuleService.get_all_modules()

# Subscribe to module
subscription = SubscriptionService.subscribe_university(
    university=university,
    module_id="module-uuid",
    start_date="2024-01-01",
    end_date="2024-12-31",
    created_by=admin_user,
    is_trial=False
)

# Get subscriptions
subscriptions = SubscriptionService.get_university_subscriptions(university)

# Check module access
has_access = SubscriptionService.check_module_access(university, "academic")

# Renew subscription
SubscriptionService.renew_subscription(
    subscription_id="subscription-uuid",
    new_end_date="2025-12-31",
    renewed_by=admin_user
)

# Cancel subscription
SubscriptionService.cancel_subscription(
    subscription_id="subscription-uuid",
    cancelled_by=admin_user
)

# Get expiring subscriptions
expiring = SubscriptionService.get_expiring_subscriptions(days=30)

# Auto-expire subscriptions
count = SubscriptionService.auto_expire_subscriptions()
```

### cURL Examples

```bash
# Get university profile
curl -X GET http://localhost:8000/api/super-admin/universities/{university_id}/profile/ \
  -H "Authorization: Bearer <token>"

# Update university profile
curl -X PUT http://localhost:8000/api/super-admin/universities/{university_id}/profile/ \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{
    "status": "active",
    "contact_email": "admin@university.edu",
    "max_users": 1500
  }'

# Get all modules
curl -X GET http://localhost:8000/api/super-admin/modules/ \
  -H "Authorization: Bearer <token>"

# Get subscriptions
curl -X GET http://localhost:8000/api/super-admin/universities/{university_id}/subscriptions/ \
  -H "Authorization: Bearer <token>"

# Create subscription
curl -X POST http://localhost:8000/api/super-admin/universities/{university_id}/subscriptions/ \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{
    "module_id": "module-uuid",
    "start_date": "2024-01-01",
    "end_date": "2024-12-31",
    "is_trial": false
  }'

# Cancel subscription
curl -X POST http://localhost:8000/api/super-admin/subscriptions/{subscription_id}/cancel/ \
  -H "Authorization: Bearer <token>"

# Renew subscription
curl -X POST http://localhost:8000/api/super-admin/subscriptions/{subscription_id}/renew/ \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{"new_end_date": "2025-12-31"}'

# Get expiring subscriptions
curl -X GET "http://localhost:8000/api/super-admin/subscriptions/expiring/?days=30" \
  -H "Authorization: Bearer <token>"
```

## Available Modules

Common modules in the system:

| Code | Name | Description |
|------|------|-------------|
| academic | Academic Management | Course, class, and academic operations |
| student | Student Management | Student enrollment and profiles |
| exam | Exam Management | Exam scheduling and results |
| document | Document Management | Document requests and management |
| finance | Finance Management | Payment and financial operations |
| infrastructure | Infrastructure | Building and room management |
| scheduling | Scheduling | Timetable and scheduling |
| notification | Notifications | Event notifications |

## Subscription Statuses

- **active**: Subscription is active and valid
- **inactive**: Subscription is inactive
- **expired**: Subscription has passed end date
- **suspended**: Subscription is suspended

## University Profile Statuses

- **active**: University is active
- **inactive**: University is inactive
- **suspended**: University is suspended
- **trial**: University is in trial period

## Best Practices

1. **Profile Setup**: Complete university profile immediately after creation
2. **Module Selection**: Subscribe to required modules based on needs
3. **Renewal Tracking**: Monitor expiring subscriptions
4. **Trial Periods**: Use trial subscriptions for testing
5. **Resource Limits**: Set appropriate user and storage limits
6. **Audit Review**: Monitor subscription changes

## Monitoring

### Check Subscription Status
```python
from services.dependent_service.dashboard_module.dashboard_super_admin_app.models import UniversitySubscription

# Active subscriptions
active = UniversitySubscription.objects.filter(status="active")

# Expired subscriptions
expired = UniversitySubscription.objects.filter(status="expired")

# Expiring soon
from datetime import timedelta
from django.utils import timezone

expiry_date = timezone.now().date() + timedelta(days=30)
expiring = UniversitySubscription.objects.filter(
    status="active",
    end_date__lte=expiry_date
)
```

## Limitations

- One subscription per university per module
- Cannot have overlapping active subscriptions for same module
- End date must be after start date
- Superuser access required for management
