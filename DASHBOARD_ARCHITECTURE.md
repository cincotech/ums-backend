# Dashboard Architecture - Super Admin vs University Admin

## 🏗️ Architecture Overview

Le système UMS utilise une architecture à deux niveaux d'administration :

### 1. **Super Admin** 🔴
- Gère l'**ensemble du système**
- Accès à toutes les universités
- Contrôle complet des configurations système
- Gestion des sauvegardes et restaurations
- Audit de sécurité global
- Gestion des administrateurs universitaires

### 2. **University Admin** 🟢
- Gère une **université spécifique**
- Accès limité à son université
- Gestion des utilisateurs universitaires
- Gestion académique et financière
- Rapports universitaires
- Audit limité à son université

---

## 📊 Modèles de données

### SuperAdminProfile
```python
- user: OneToOneField(User)
- admin_role: ForeignKey(SuperAdminRole)
- status: active/inactive/suspended
- Permissions: Toutes les opérations système
```

### UniversityAdminProfile
```python
- user: OneToOneField(User)
- university: ForeignKey(University)
- status: active/inactive/suspended
- can_manage_users: Boolean
- can_manage_academic: Boolean
- can_manage_finance: Boolean
- can_manage_infrastructure: Boolean
- can_view_reports: Boolean
```

---

## 🔐 Permissions

### IsSuperAdmin
- Vérifie si l'utilisateur a un profil Super Admin actif
- Accès à tous les endpoints système

### IsUniversityAdmin
- Vérifie si l'utilisateur a un profil University Admin actif
- Accès limité à son université

### CanManageUsers, CanManageAcademic, CanManageFinance
- Permissions granulaires pour University Admin
- Super Admin a toutes les permissions

---

## 📡 Endpoints API

### Super Admin Dashboard

#### Overview
```
GET /dashboard/super-admin/overview/
```
Retourne :
- total_universities
- total_users
- active_users
- total_admins
- failed_logins_24h
- pending_backups

#### System Health
```
GET /dashboard/super-admin/system_health/
```
Retourne :
- database_status
- backup_status
- security_alerts
- active_sessions

#### Audit Logs
```
GET /dashboard/super-admin/audit_logs/
```
Retourne les 50 derniers logs d'audit

#### Backups
```
GET /dashboard/super-admin/backups/
POST /dashboard/super-admin/initiate_backup/
```
Gestion des sauvegardes système

#### System Configuration
```
GET /dashboard/super-admin/system_config/
POST /dashboard/super-admin/update_system_config/
```
Gestion des configurations système

---

### University Admin Dashboard

#### Overview
```
GET /dashboard/university-admin/overview/
```
Retourne :
- university_name
- total_users
- active_users
- total_departments
- total_students
- total_teachers

#### Users
```
GET /dashboard/university-admin/users/?page=1&limit=20
```
Liste paginée des utilisateurs de l'université

#### Reports
```
GET /dashboard/university-admin/reports/
```
Rapports académiques et financiers

#### Audit Logs
```
GET /dashboard/university-admin/audit_logs/
```
Logs d'audit de l'université

---

## 🔄 Flux d'authentification

### Super Admin
1. Connexion avec email/password
2. Vérification du profil SuperAdminProfile
3. Accès au dashboard système complet

### University Admin
1. Connexion avec email/password
2. Vérification du profil UniversityAdminProfile
3. Accès au dashboard de son université

---

## 📋 Modèles de support

### SystemConfiguration
- Configurations globales du système
- Catégories : academic_year, fee_type, feature, security, etc.
- Peut être système-wide ou université-spécifique

### SecurityAuditLog
- Logs de toutes les actions système
- Sévérité : info, warning, error, critical
- Traçabilité complète des modifications

### BackupRecord
- Gestion des sauvegardes
- Types : full, incremental, differential
- Statut : pending, running, completed, failed

### SuperAdminRole
- Rôles spécialisés pour administrateurs
- Types : super_admin, user_admin, service_admin, security_admin, academic_admin, financial_admin
- Permissions granulaires

### EmergencyRecovery
- Opérations de récupération d'urgence
- Types : password_reset, account_unlock, role_restoration, data_recovery, system_restore

---

## 🛡️ Sécurité

### Isolation des données
- Super Admin : Accès global
- University Admin : Accès limité à son université
- Filtrage automatique des requêtes

### Audit complet
- Chaque action est enregistrée
- IP, User Agent, Localisation
- Succès/Échec et messages d'erreur

### Gestion des comptes
- Verrouillage après tentatives échouées
- Statut : active/inactive/suspended
- Historique des connexions

---

## 📈 Cas d'usage

### Super Admin
1. **Monitoring système** : Vérifier la santé du système
2. **Gestion des universités** : Ajouter/modifier/supprimer universités
3. **Gestion des administrateurs** : Créer/modifier les admins universitaires
4. **Sauvegardes** : Initier des sauvegardes complètes
5. **Audit** : Consulter tous les logs du système
6. **Configuration** : Modifier les paramètres globaux

### University Admin
1. **Gestion des utilisateurs** : Ajouter/modifier/supprimer utilisateurs
2. **Gestion académique** : Gérer les programmes, cours, etc.
3. **Gestion financière** : Gérer les frais, paiements
4. **Rapports** : Générer des rapports universitaires
5. **Audit** : Consulter les logs de son université

---

## 🚀 Intégration

### Dans urls.py principal
```python
path("dashboard/", include("services.dependent_service.dashboard_module.dashboard_super_admin_app.urls"))
```

### Utilisation dans les vues
```python
from .permissions import IsSuperAdmin, IsUniversityAdmin

class MyViewSet(viewsets.ViewSet):
    permission_classes = [IsAuthenticated, IsSuperAdmin]
```

---

## 📝 Exemple d'utilisation

### Créer un Super Admin
```python
from services.dependent_service.dashboard_module.dashboard_super_admin_app.models import (
    SuperAdminProfile, SuperAdminRole
)

role = SuperAdminRole.objects.create(
    name="System Administrator",
    role_type="super_admin",
    description="Full system access",
    can_manage_users=True,
    can_manage_roles=True,
    can_manage_system_config=True,
    can_view_audit_logs=True,
    can_manage_backups=True,
    created_by=admin_user
)

SuperAdminProfile.objects.create(
    user=user,
    admin_role=role,
    status="active",
    created_by=admin_user
)
```

### Créer un University Admin
```python
from services.dependent_service.dashboard_module.dashboard_super_admin_app.models import (
    UniversityAdminProfile
)

UniversityAdminProfile.objects.create(
    user=user,
    university=university,
    status="active",
    can_manage_users=True,
    can_manage_academic=True,
    can_manage_finance=True,
    can_view_reports=True,
    created_by=super_admin_user
)
```

---

## 🔍 Monitoring

### Vérifier la santé du système
```bash
GET /dashboard/super-admin/system_health/
```

### Consulter les logs d'audit
```bash
GET /dashboard/super-admin/audit_logs/
```

### Initier une sauvegarde
```bash
POST /dashboard/super-admin/initiate_backup/
{
    "backup_type": "full"
}
```

---

## 📞 Support

Pour toute question sur l'architecture des dashboards, consultez :
- Documentation API Swagger
- Logs d'audit du système
- Interface admin Django
