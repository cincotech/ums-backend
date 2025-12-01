# Secure Backup & Restore Implementation

## Overview

Implemented secure encrypted backup and restore functionality for both Super Admin and University Admin using django-dbbackup with Fernet encryption.

## Architecture

### Models Used (from super_admin_app)

1. **BackupRecord**
   - Tracks all backup operations
   - Stores encrypted file path and metadata
   - Records backup type, status, timestamps
   - Stores university_id in metadata for scoping

2. **EmergencyRecovery**
   - Tracks all restore operations
   - Records recovery type, status, results
   - Maintains audit trail of who performed restore

3. **AuditLog**
   - Logs all backup/restore actions
   - Records success/failure with error messages
   - Scoped to university for admin visibility

### Service Layer

**SecureBackupService** (`backup_service.py`)
- `create_backup(university, initiated_by)`: Create encrypted backup
- `restore_backup(backup_record, performed_by)`: Restore from encrypted backup
- `get_university_backups(university)`: List backups for university
- `delete_backup(backup_record)`: Securely delete backup file

### API Endpoints

```
POST   /api/admin/dashboard/backups/              - Create backup
GET    /api/admin/dashboard/backups/              - List backups
POST   /api/admin/dashboard/backups/{id}/restore/ - Restore backup
DELETE /api/admin/dashboard/backups/{id}/         - Delete backup
```

## Security Features

### Encryption

- **Algorithm**: Fernet (symmetric encryption)
- **Key Source**: Environment variable `BACKUP_ENCRYPTION_KEY`
- **File Format**: `.enc` (encrypted dump files)
- **Key Generation**: `Fernet.generate_key()`

### Access Control

- University admins can only backup/restore their own university
- All endpoints require authentication
- Automatic university scoping via `get_admin_university()`
- Super admin models used but accessed through admin app

### Secure Deletion

```python
# Overwrite file with random data before deletion
with open(backup_record.file_path, "wb") as f:
    f.write(os.urandom(os.path.getsize(backup_record.file_path)))
os.remove(backup_record.file_path)
```

### Audit Logging

All operations logged with:
- User who initiated action
- University affected
- Action type (backup_initiated, restore_initiated)
- Success/failure status
- Error messages if failed
- Timestamp

## Configuration

### Django Settings (`ums/settings/base.py`)

```python
INSTALLED_APPS = [
    ...
    "dbbackup",
    ...
]

DBBACKUP_BACKUP_DIRECTORY = os.path.join(BASE_DIR, "backups")
DBBACKUP_STORAGE = "django.core.files.storage.FileSystemStorage"
DBBACKUP_STORAGE_OPTIONS = {"location": DBBACKUP_BACKUP_DIRECTORY}
DBBACKUP_CLEANUP_KEEP = 10
DBBACKUP_FILENAME_TEMPLATE = "backup_{datetime}.dump"
DBBACKUP_ENCRYPTION_KEY = os.getenv("BACKUP_ENCRYPTION_KEY", None)
```

### Environment Variables

```env
BACKUP_ENCRYPTION_KEY=<fernet-key>
```

Generate key:
```bash
python -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())"
```

## File Structure

```
dashboard_admin_app/
├── backup_service.py              # Secure backup/restore service
├── views.py                        # API endpoints (backup_list, restore_backup, delete_backup)
├── serializers.py                  # BackupRecordSerializer, EmergencyRecoverySerializer
├── urls.py                         # Backup/restore URL patterns
├── BACKUP_RESTORE_GUIDE.md        # User documentation
└── management/
    └── commands/
        └── backup_universities.py  # Management command for scheduled backups
```

## Usage

### Create Backup

```bash
curl -X POST http://localhost:8000/api/admin/dashboard/backups/ \
  -H "Authorization: Bearer <token>"
```

### List Backups

```bash
curl -X GET http://localhost:8000/api/admin/dashboard/backups/ \
  -H "Authorization: Bearer <token>"
```

### Restore Backup

```bash
curl -X POST http://localhost:8000/api/admin/dashboard/backups/{backup_id}/restore/ \
  -H "Authorization: Bearer <token>"
```

### Delete Backup

```bash
curl -X DELETE http://localhost:8000/api/admin/dashboard/backups/{backup_id}/ \
  -H "Authorization: Bearer <token>"
```

### Management Command

```bash
# Backup all universities
python manage.py backup_universities

# Backup specific university
python manage.py backup_universities --university-id <uuid>
```

## Data Flow

### Backup Process

1. Admin calls POST `/api/admin/dashboard/backups/`
2. `backup_list()` view extracts university from admin profile
3. `SecureBackupService.create_backup()` called
4. django-dbbackup creates database dump
5. Dump encrypted with Fernet using environment key
6. Encrypted file saved to `backups/` directory
7. BackupRecord created with metadata
8. AuditLog entry created
9. Response returned with backup details

### Restore Process

1. Admin calls POST `/api/admin/dashboard/backups/{id}/restore/`
2. `restore_backup()` view validates university access
3. `SecureBackupService.restore_backup()` called
4. Encrypted backup file read
5. File decrypted using environment key
6. Decrypted data written to temp file
7. django-dbbackup restores database
8. Temp file deleted
9. EmergencyRecovery record created
10. AuditLog entry created
11. Response returned with recovery details

## Backup Models Integration

### Why Use Super Admin Models?

1. **Centralized Audit Trail**: All backup/restore operations in one place
2. **System-Wide Visibility**: Super admin can see all backups
3. **Consistent Logging**: Uses same AuditLog model as system
4. **No Duplication**: Avoids creating separate models
5. **Scalability**: Supports multiple universities

### Model Relationships

```
BackupRecord
├── initiated_by → User
└── metadata → {"university_id": "...", "university_name": "..."}

EmergencyRecovery
├── performed_by → User
└── details → {"backup_id": "..."}

AuditLog
├── user → User
├── university → University
└── Tracks all backup/restore actions
```

## Security Considerations

1. **Encryption Key Management**
   - Store in environment variables
   - Never commit to version control
   - Rotate periodically
   - Keep secure backup of keys

2. **File Permissions**
   - Backup directory should be restricted
   - Only application user can read/write
   - Regular permission audits

3. **Access Control**
   - University admins isolated to their data
   - Super admin can see all backups
   - All operations require authentication

4. **Audit Trail**
   - All operations logged
   - Logs retained for compliance
   - Regular audit log reviews

## Monitoring & Maintenance

### Check Backup Status

```python
from services.dependent_service.dashboard_module.dashboard_super_admin_app.models import BackupRecord

# Recent backups
BackupRecord.objects.order_by('-started_at')[:10]

# Failed backups
BackupRecord.objects.filter(status='failed')

# Backup size
BackupRecord.objects.aggregate(Sum('file_size'))
```

### Cleanup Old Backups

```bash
python manage.py dbbackup --cleanup
```

Configured to keep 10 most recent backups (DBBACKUP_CLEANUP_KEEP = 10)

## Troubleshooting

### Backup Creation Failed

Check:
- Disk space: `df -h`
- Database connectivity
- Encryption key set: `echo $BACKUP_ENCRYPTION_KEY`
- Directory permissions: `ls -la backups/`

### Restore Failed

Check:
- Backup file exists: `ls -la backups/`
- Encryption key matches
- Database accessible
- No active connections

### Encryption Issues

```python
from cryptography.fernet import Fernet

# Verify key format
key = os.getenv("BACKUP_ENCRYPTION_KEY")
Fernet(key.encode())  # Should not raise error
```

## Dependencies

```
django-dbbackup==4.0.2
cryptography>=3.4
```

## Next Steps

1. Set up scheduled backups using Celery or cron
2. Implement backup retention policies
3. Add backup verification/integrity checks
4. Set up offsite backup storage
5. Create backup restore testing procedures
6. Document disaster recovery procedures
