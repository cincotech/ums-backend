# Audit Service - System-Wide Usage Guide

## Overview

The audit service is a centralized logging system available to all modules in the UMS. It tracks all user activities, system changes, and security events.

## Location

```
services/core_service/audit_service.py
```

## Import

```python
from services.core_service.audit_service import (
    log_audit,
    log_user_action,
    log_security_event,
    log_create,
    log_update,
    log_delete,
    log_config_change,
    log_backup_action,
    log_emergency_recovery,
    log_login,
    log_logout,
    log_permission_change,
    log_role_change,
)
```

## Available Functions

### 1. Core Logging

#### `log_audit(user, action, description, ...)`
Main audit logging function with full control

```python
log_audit(
    user=request.user,
    action="create",
    description="Created new student",
    entity_type="Student",
    entity_id=student.id,
    changes={"name": student.name, "email": student.email},
    request=request,
    severity="info",
    success=True,
)
```

#### `log_user_action(request, action, description, ...)`
Log user actions with automatic request context

```python
log_user_action(
    request,
    action="update",
    description="Updated course information",
    entity_type="Course",
    entity_id=course.id,
    changes={"title": "New Title"},
)
```

#### `log_security_event(request, action, description, ...)`
Log security-related events

```python
log_security_event(
    request,
    action="failed_login",
    description="Failed login attempt",
    severity="warning",
    success=False,
    error_message="Invalid credentials",
)
```

### 2. Entity Operations

#### `log_create(request, entity_type, entity_id, description, changes)`
Log entity creation

```python
log_create(
    request,
    entity_type="University",
    entity_id=university.id,
    description="Created new university",
    changes={"name": university.name},
)
```

#### `log_update(request, entity_type, entity_id, description, old_value, new_value)`
Log entity updates

```python
log_update(
    request,
    entity_type="User",
    entity_id=user.id,
    description="Updated user email",
    old_value=old_email,
    new_value=new_email,
)
```

#### `log_delete(request, entity_type, entity_id, description)`
Log entity deletion

```python
log_delete(
    request,
    entity_type="Course",
    entity_id=course.id,
    description="Deleted course",
)
```

### 3. Specialized Logging

#### `log_config_change(request, category, key, old_value, new_value)`
Log configuration changes

```python
log_config_change(
    request,
    category="academic",
    key="semester_duration",
    old_value=16,
    new_value=18,
)
```

#### `log_backup_action(request, backup_id, action, status, error_message)`
Log backup operations

```python
log_backup_action(
    request,
    backup_id=backup.id,
    action="initiated",
    status="running",
)
```

#### `log_emergency_recovery(request, recovery_id, recovery_type, status, result)`
Log emergency recovery operations

```python
log_emergency_recovery(
    request,
    recovery_id=recovery.id,
    recovery_type="password_reset",
    status="completed",
)
```

#### `log_login(request, user, success, error_message)`
Log login attempts

```python
log_login(
    request,
    user=user,
    success=True,
)
```

#### `log_logout(request)`
Log user logout

```python
log_logout(request)
```

#### `log_permission_change(request, user_id, old_permissions, new_permissions)`
Log permission changes

```python
log_permission_change(
    request,
    user_id=user.id,
    old_permissions=["read"],
    new_permissions=["read", "write"],
)
```

#### `log_role_change(request, user_id, old_role, new_role)`
Log role changes

```python
log_role_change(
    request,
    user_id=user.id,
    old_role="Student",
    new_role="Teacher",
)
```

## Usage Examples

### In Views

```python
from rest_framework.views import APIView
from services.core_service.audit_service import log_user_action, log_security_event

class StudentCreateView(APIView):
    def post(self, request):
        try:
            student = Student.objects.create(**request.data)
            log_user_action(
                request,
                action="create",
                description=f"Created student: {student.name}",
                entity_type="Student",
                entity_id=student.id,
            )
            return Response({"success": True})
        except Exception as e:
            log_security_event(
                request,
                action="create",
                description=f"Failed to create student",
                severity="error",
                success=False,
                error_message=str(e),
            )
            return Response({"error": str(e)}, status=400)
```

### In Serializers

```python
from services.core_service.audit_service import log_update

class CourseSerializer(serializers.ModelSerializer):
    def update(self, instance, validated_data):
        old_title = instance.title
        instance = super().update(instance, validated_data)

        log_update(
            self.context['request'],
            entity_type="Course",
            entity_id=instance.id,
            description="Updated course",
            old_value=old_title,
            new_value=instance.title,
        )
        return instance
```

### In Models (Signals)

```python
from django.db.models.signals import post_save
from django.dispatch import receiver
from services.core_service.audit_service import log_create

@receiver(post_save, sender=User)
def log_user_creation(sender, instance, created, **kwargs):
    if created:
        # Note: request not available in signals, use None
        log_audit(
            user=None,
            action="create",
            description=f"User created: {instance.email}",
            entity_type="User",
            entity_id=instance.id,
        )
```

## Audit Log Fields

Each audit log entry contains:

- `id` - Unique identifier
- `user` - User who performed the action
- `action` - Type of action (login, create, update, delete, etc.)
- `severity` - Severity level (info, warning, error, critical)
- `entity_type` - Type of entity affected
- `entity_id` - ID of entity affected
- `description` - Human-readable description
- `changes` - JSON object with detailed changes
- `ip_address` - Client IP address
- `user_agent` - Client user agent
- `location` - Geographic location (if available)
- `success` - Whether action succeeded
- `error_message` - Error message if failed
- `university` - Associated university (if applicable)
- `timestamp` - When action occurred

## Querying Audit Logs

```python
from services.dependent_service.dashboard_module.dashboard_super_admin_app.models import AuditLog

# Get all actions by a user
logs = AuditLog.objects.filter(user=user)

# Get all failed operations
failed = AuditLog.objects.filter(success=False)

# Get security events
security = AuditLog.objects.filter(severity__in=["warning", "critical"])

# Get actions in last 24 hours
from django.utils import timezone
from datetime import timedelta
recent = AuditLog.objects.filter(
    timestamp__gte=timezone.now() - timedelta(hours=24)
)

# Get university-specific logs
uni_logs = AuditLog.objects.filter(university=university)
```

## Best Practices

1. **Always include request context** - Pass the request object when available
2. **Use specific action types** - Choose from predefined ACTION_TYPES
3. **Include entity information** - Always specify entity_type and entity_id
4. **Log changes** - Include old and new values for updates
5. **Set appropriate severity** - Use warning/critical for important events
6. **Handle errors** - Log failed operations with error messages
7. **Be descriptive** - Write clear, meaningful descriptions

## Security Considerations

- Audit logs are immutable (read-only in admin)
- All user actions are tracked with IP and user agent
- Failed operations are logged for security analysis
- Sensitive data should not be logged in changes field
- Regular audit log review is recommended

## Performance

- Audit logs are indexed by user, timestamp, action, and severity
- Queries are optimized for dashboard and reporting
- Consider archiving old logs periodically
- Use filters to limit query results

---

**Note**: This service is available system-wide and should be used consistently across all modules for comprehensive audit trails.
