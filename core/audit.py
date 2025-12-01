"""
Centralized audit logging service for the entire UMS system
Available to all modules for tracking activities and maintaining audit trails
"""

from django.http import HttpRequest

from services.dependent_service.dashboard_module.dashboard_super_admin_app.models import (
    AuditLog,
)


def get_client_ip(request: HttpRequest) -> str:
    """Extract client IP from request"""
    x_forwarded_for = request.META.get("HTTP_X_FORWARDED_FOR")
    if x_forwarded_for:
        return x_forwarded_for.split(",")[0].strip()
    return request.META.get("REMOTE_ADDR", "")


def get_user_agent(request: HttpRequest) -> str:
    """Extract user agent from request"""
    return request.META.get("HTTP_USER_AGENT", "")[:500]


def log_audit(
    user,
    action,
    description,
    severity="info",
    entity_type=None,
    entity_id=None,
    changes=None,
    request=None,
    university=None,
    success=True,
    error_message=None,
):
    """Log audit activity to database"""
    ip_address = None
    user_agent = None

    if request:
        ip_address = get_client_ip(request)
        user_agent = get_user_agent(request)

    AuditLog.objects.create(
        user=user,
        action=action,
        severity=severity,
        entity_type=entity_type,
        entity_id=str(entity_id) if entity_id else None,
        description=description,
        changes=changes or {},
        ip_address=ip_address,
        user_agent=user_agent,
        university=university,
        success=success,
        error_message=error_message,
    )


def log_user_action(
    request, action, description, entity_type=None, entity_id=None, changes=None
):
    """Log user action with request context"""
    log_audit(
        user=request.user,
        action=action,
        description=description,
        entity_type=entity_type,
        entity_id=entity_id,
        changes=changes,
        request=request,
    )


def log_security_event(
    request, action, description, severity="warning", success=True, error_message=None
):
    """Log security-related events"""
    log_audit(
        user=request.user if request.user.is_authenticated else None,
        action=action,
        description=description,
        severity=severity,
        request=request,
        success=success,
        error_message=error_message,
    )


def log_create(request, entity_type, entity_id, description, changes=None):
    """Log entity creation"""
    log_user_action(request, "create", description, entity_type, entity_id, changes)


def log_update(request, entity_type, entity_id, description, old_value, new_value):
    """Log entity update"""
    log_user_action(
        request,
        "update",
        description,
        entity_type,
        entity_id,
        {"old_value": old_value, "new_value": new_value},
    )


def log_delete(request, entity_type, entity_id, description):
    """Log entity deletion"""
    log_user_action(request, "delete", description, entity_type, entity_id)


def log_config_change(request, category, key, old_value, new_value):
    """Log configuration changes"""
    log_audit(
        user=request.user,
        action="config_change",
        description=f"Configuration changed: {category}/{key}",
        entity_type="SystemConfiguration",
        entity_id=f"{category}:{key}",
        changes={"old_value": old_value, "new_value": new_value},
        request=request,
    )


def log_backup_action(request, backup_id, action, status, error_message=None):
    """Log backup-related actions"""
    log_audit(
        user=request.user,
        action="backup_initiated" if action == "initiated" else "restore_initiated",
        description=f"Backup {action}: {status}",
        entity_type="BackupRecord",
        entity_id=backup_id,
        request=request,
        success=status == "completed",
        error_message=error_message,
    )


def log_emergency_recovery(request, recovery_id, recovery_type, status, result=None):
    """Log emergency recovery actions"""
    log_audit(
        user=request.user,
        action="password_reset" if recovery_type == "password_reset" else "update",
        description=f"Emergency recovery: {recovery_type} - {status}",
        entity_type="EmergencyRecovery",
        entity_id=recovery_id,
        changes={"recovery_type": recovery_type, "status": status},
        request=request,
        success=status == "completed",
        error_message=result if status == "failed" else None,
    )


def log_login(request, user, success=True, error_message=None):
    """Log login attempts"""
    log_audit(
        user=user,
        action="login",
        description="User login",
        severity="info" if success else "warning",
        request=request,
        success=success,
        error_message=error_message,
    )


def log_logout(request):
    """Log logout"""
    log_audit(
        user=request.user,
        action="logout",
        description="User logout",
        request=request,
    )


def log_permission_change(request, user_id, old_permissions, new_permissions):
    """Log permission changes"""
    log_audit(
        user=request.user,
        action="permission_change",
        description=f"Permissions changed for user {user_id}",
        entity_type="User",
        entity_id=user_id,
        changes={
            "old_permissions": old_permissions,
            "new_permissions": new_permissions,
        },
        request=request,
        severity="warning",
    )


def log_role_change(request, user_id, old_role, new_role):
    """Log role changes"""
    log_audit(
        user=request.user,
        action="role_change",
        description=f"Role changed for user {user_id}: {old_role} → {new_role}",
        entity_type="User",
        entity_id=user_id,
        changes={"old_role": old_role, "new_role": new_role},
        request=request,
        severity="warning",
    )
