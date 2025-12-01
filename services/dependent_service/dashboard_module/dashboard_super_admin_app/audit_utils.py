"""
Deprecated: Use core.audit instead
This module is kept for backward compatibility
"""

from core.audit import (
    log_audit,
    log_backup_action,
    log_config_change,
    log_create,
    log_delete,
    log_emergency_recovery,
    log_login,
    log_logout,
    log_permission_change,
    log_role_change,
    log_security_event,
    log_update,
    log_user_action,
)

__all__ = [
    "log_audit",
    "log_user_action",
    "log_security_event",
    "log_create",
    "log_update",
    "log_delete",
    "log_config_change",
    "log_backup_action",
    "log_emergency_recovery",
    "log_login",
    "log_logout",
    "log_permission_change",
    "log_role_change",
]
