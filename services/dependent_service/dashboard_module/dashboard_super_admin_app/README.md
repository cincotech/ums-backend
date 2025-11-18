# Super Administrator Dashboard

Dashboard specifically designed for Super Administrator role with comprehensive system management capabilities.

## Use Cases

### 1. Gestion des utilisateurs
**Description**: Créer, modifier, activer/désactiver et supprimer des comptes pour tous les autres acteurs, y compris l'attribution des rôles.

**Endpoints**:
- `GET /dashboard/super-admin/users/` - List all users
- `POST /dashboard/super-admin/users/` - Create new user
- `PUT /dashboard/super-admin/users/{user_id}/` - Update user
- `PATCH /dashboard/super-admin/users/{user_id}/` - Toggle user active status
- `DELETE /dashboard/super-admin/users/{user_id}/` - Delete user

### 2. Gestion des Administrateurs
**Description**: Créer, attribuer, modifier et supprimer les autres rôles d'administrateur.

**Endpoints**:
- `GET /dashboard/super-admin/roles/` - List all roles
- `POST /dashboard/super-admin/roles/` - Create new role
- `PUT /dashboard/super-admin/roles/{role_id}/` - Update role
- `DELETE /dashboard/super-admin/roles/{role_id}/` - Delete role

### 3. Configuration du système
**Description**: Gérer les paramètres globaux de l'application (années académiques, types de frais, fonctionnalités, configurations de sécurité).

**Endpoints**:
- `GET /dashboard/super-admin/config/` - List system configurations
- `POST /dashboard/super-admin/config/` - Create configuration
- `PUT /dashboard/super-admin/config/{config_id}/` - Update configuration
- `DELETE /dashboard/super-admin/config/{config_id}/` - Delete configuration

### 4. Sécurité et Urgence
**Description**: Réinitialiser des mots de passe pour d'autres administrateurs, gérer la sécurité globale du compte.

**Endpoints**:
- `POST /dashboard/super-admin/users/{user_id}/reset-password/` - Reset user password

### 5. Audit et journalisation
**Description**: Consulter les journaux d'activité pour surveiller les actions critiques du système.

**Endpoints**:
- `GET /dashboard/super-admin/audit-logs/` - Get audit logs

### 6. Sauvegarde/Restauration
**Description**: Déclencher et gérer les processus de sauvegarde et de restauration de la base de données.

**Endpoints**:
- `POST /dashboard/super-admin/backup/` - Initiate backup
- `GET /dashboard/super-admin/backup/history/` - Get backup history

## API Endpoints

### Dashboard Overview
```
GET /dashboard/super-admin/overview/
```
Returns super admin dashboard statistics.

### User Management
```
GET /dashboard/super-admin/users/
POST /dashboard/super-admin/users/
PUT /dashboard/super-admin/users/{user_id}/
PATCH /dashboard/super-admin/users/{user_id}/
DELETE /dashboard/super-admin/users/{user_id}/
```

### Role Management
```
GET /dashboard/super-admin/roles/
POST /dashboard/super-admin/roles/
PUT /dashboard/super-admin/roles/{role_id}/
DELETE /dashboard/super-admin/roles/{role_id}/
```

### System Configuration
```
GET /dashboard/super-admin/config/
POST /dashboard/super-admin/config/
PUT /dashboard/super-admin/config/{config_id}/
DELETE /dashboard/super-admin/config/{config_id}/
```

### Security & Emergency
```
POST /dashboard/super-admin/users/{user_id}/reset-password/
```

### Backup Management
```
POST /dashboard/super-admin/backup/
GET /dashboard/super-admin/backup/history/
```

### Audit Logs
```
GET /dashboard/super-admin/audit-logs/
```

## Models

### SystemConfiguration
Stores system-wide configuration settings.

### AuditLog
Tracks all critical system actions for security monitoring.

### BackupRecord
Records backup operations and their status.

## Installation

1. Add `services.dependent_service.dashboard_module.dashboard_super_admin_app` to `INSTALLED_APPS`
2. Run migrations: `python manage.py makemigrations dashboard_super_admin_app && python manage.py migrate`

## Usage

All endpoints require Super Administrator authentication.

Example usage:
```python
# Create user
response = requests.post('/dashboard/super-admin/users/',
                        json={'email': 'user@example.com', 'password': 'pass123'},
                        headers={'Authorization': 'Bearer <token>'})

# Reset password
response = requests.post('/dashboard/super-admin/users/{id}/reset-password/',
                        json={'new_password': 'newpass123'},
                        headers={'Authorization': 'Bearer <token>'})
```
