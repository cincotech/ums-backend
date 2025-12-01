# Secure Backup & Restore Guide

## Overview

The UMS system provides secure encrypted backup and restore functionality for university data. All backups are encrypted using Fernet encryption and stored securely.

## Features

- **Encrypted Backups**: All backups are encrypted with Fernet encryption
- **University-Scoped**: Each admin can only backup/restore their own university
- **Audit Logging**: All backup/restore operations are logged
- **Secure Deletion**: Backup files are securely overwritten before deletion
- **django-dbbackup Integration**: Uses industry-standard backup tool

## Setup

### 1. Install Dependencies

```bash
pip install django-dbbackup cryptography
```

### 2. Environment Configuration

Add to `.env`:

```env
BACKUP_ENCRYPTION_KEY=<your-encryption-key>
```

Generate a key if needed:

```python
from cryptography.fernet import Fernet
key = Fernet.generate_key()
print(key.decode())
```

### 3. Django Settings

Already configured in `ums/settings/base.py`:

```python
DBBACKUP_BACKUP_DIRECTORY = os.path.join(BASE_DIR, "backups")
DBBACKUP_STORAGE = "django.core.files.storage.FileSystemStorage"
DBBACKUP_STORAGE_OPTIONS = {"location": DBBACKUP_BACKUP_DIRECTORY}
DBBACKUP_CLEANUP_KEEP = 10
DBBACKUP_FILENAME_TEMPLATE = "backup_{datetime}.dump"
```

## API Endpoints

### Create Backup

```
POST /api/admin/dashboard/backups/
Authorization: Bearer <token>
```

**Response:**
```json
{
  "success": true,
  "data": {
    "id": "uuid",
    "backup_type": "full",
    "status": "completed",
    "file_path": "backups/backup_2024-01-15.enc",
    "file_size": 5242880,
    "initiated_by_email": "admin@university.edu",
    "started_at": "2024-01-15T10:30:00Z",
    "completed_at": "2024-01-15T10:35:00Z"
  }
}
```

### List Backups

```
GET /api/admin/dashboard/backups/
Authorization: Bearer <token>
```

Returns all backups for the admin's university.

### Restore Backup

```
POST /api/admin/dashboard/backups/{backup_id}/restore/
Authorization: Bearer <token>
```

**Response:**
```json
{
  "success": true,
  "data": {
    "id": "uuid",
    "recovery_type": "data_recovery",
    "status": "completed",
    "reason": "Restoring from backup {backup_id}",
    "result": "Successfully restored data for University Name",
    "performed_by_email": "admin@university.edu",
    "initiated_at": "2024-01-15T10:40:00Z",
    "completed_at": "2024-01-15T10:45:00Z"
  }
}
```

### Delete Backup

```
DELETE /api/admin/dashboard/backups/{backup_id}/
Authorization: Bearer <token>
```

Securely deletes backup file (overwrites before deletion).

## Security Features

### Encryption

- **Algorithm**: Fernet (symmetric encryption)
- **Key Management**: Environment variable based
- **File Format**: `.enc` (encrypted dump files)

### Access Control

- Only university admins can backup/restore their university
- All operations require authentication
- Automatic university scoping

### Audit Trail

All operations logged with:
- User who initiated action
- University affected
- Timestamp
- Success/failure status
- Error messages if failed

### Secure Deletion

Backup files are securely overwritten with random data before deletion to prevent recovery.

## Usage Examples

### Python/Django

```python
from services.dependent_service.dashboard_module.dashboard_admin_app.backup_service import SecureBackupService
from services.core_service.academic_module.university_app.models import University

university = University.objects.first()
admin_user = university.admin_user

# Create backup
backup = SecureBackupService.create_backup(university, admin_user)
print(f"Backup created: {backup.id}")

# Get backups
backups = SecureBackupService.get_university_backups(university)
for backup in backups:
    print(f"{backup.id}: {backup.status}")

# Restore backup
recovery = SecureBackupService.restore_backup(backup, admin_user)
print(f"Recovery status: {recovery.status}")

# Delete backup
SecureBackupService.delete_backup(backup)
```

### cURL Examples

```bash
# Create backup
curl -X POST http://localhost:8000/api/admin/dashboard/backups/ \
  -H "Authorization: Bearer <token>"

# List backups
curl -X GET http://localhost:8000/api/admin/dashboard/backups/ \
  -H "Authorization: Bearer <token>"

# Restore backup
curl -X POST http://localhost:8000/api/admin/dashboard/backups/{backup_id}/restore/ \
  -H "Authorization: Bearer <token>"

# Delete backup
curl -X DELETE http://localhost:8000/api/admin/dashboard/backups/{backup_id}/ \
  -H "Authorization: Bearer <token>"
```

## Backup Models

### BackupRecord (from super_admin_app)

Tracks all backup operations:
- `backup_type`: full, incremental, differential
- `status`: pending, running, completed, failed
- `file_path`: Path to encrypted backup file
- `file_size`: Size of encrypted file
- `initiated_by`: User who created backup
- `started_at`: When backup started
- `completed_at`: When backup completed
- `error_message`: Error details if failed
- `metadata`: Additional data (university_id, university_name, encrypted flag)

### EmergencyRecovery (from super_admin_app)

Tracks all restore operations:
- `recovery_type`: data_recovery
- `status`: pending, in_progress, completed, failed
- `performed_by`: User who initiated restore
- `reason`: Why restore was performed
- `result`: Result message
- `initiated_at`: When restore started
- `completed_at`: When restore completed

## Best Practices

1. **Regular Backups**: Schedule daily backups
2. **Test Restores**: Periodically test backup restoration
3. **Secure Keys**: Keep encryption keys in secure environment variables
4. **Monitor Logs**: Check audit logs for backup/restore operations
5. **Retention Policy**: Keep 10 most recent backups (configurable)
6. **Offsite Storage**: Consider copying backups to external storage

## Troubleshooting

### Backup Creation Failed

Check:
- Disk space available
- Database connectivity
- Encryption key configured
- File permissions on backup directory

### Restore Failed

Check:
- Backup file exists and is readable
- Encryption key matches
- Database is accessible
- No active connections to database

### Encryption Key Issues

If key is lost:
1. Generate new key: `Fernet.generate_key()`
2. Update `.env` with new key
3. Old backups cannot be restored (keep secure backup of keys)

## Monitoring

Monitor backup operations via:

1. **API Endpoints**: Check backup status
2. **Audit Logs**: View all operations
3. **Database**: Query BackupRecord and EmergencyRecovery models
4. **File System**: Check backup directory size

## Compliance

- All backups encrypted at rest
- All operations audited
- University data isolation maintained
- Secure deletion implemented
- Encryption keys managed securely
