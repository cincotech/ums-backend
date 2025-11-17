# Student Services Dashboard

Dashboard specifically designed for the Service des Étudiants role - the central administrative interface for student academic and extra-academic life. This role acts as data manager, compliance controller, and central administrative contact point.

## Use Cases

### 1. Gestion des Inscriptions
**Description**: Inscrire les nouveaux étudiants après leur admission. Vérifier et valider les pièces justificatives fournies.

**Endpoints**:
- `GET /dashboard/student-services/overview/` - Dashboard overview
- Student enrollment management (integrated with existing inscription system)

### 2. Gestion des Réinscriptions
**Description**: Gérer le processus annuel de réinscription. Vérifier la conformité académique et financière.

**Endpoints**:
- Re-enrollment management (integrated with existing system)

### 3. Gestion des cas spéciaux
**Description**: Abandons, annulation de l'année académique, exclusion, etc.

**Endpoints**:
- Special case management (integrated workflows)

### 4. Traitement des Demandes de Documents
**Description**: Recevoir, vérifier l'éligibilité et produire/valider les demandes des étudiants pour diplômes, attestations, etc.

**Endpoints**:
- `GET/POST /dashboard/student-services/documents/` - Document requests management
- `POST /dashboard/student-services/documents/{request_id}/process/` - Process document requests

### 5. Gestion des Justifications d'Absence
**Description**: Recevoir et enregistrer les justifications d'absence des étudiants. Transmettre l'information aux professeurs concernés.

**Endpoints**:
- `GET/POST /dashboard/student-services/absences/` - Absence justifications
- `POST /dashboard/student-services/absences/{absence_id}/process/` - Process absence justifications

### 6. Orientation et Conseil
**Description**: Planifier et enregistrer les sessions d'orientation et de conseil académique.

**Endpoints**:
- `GET/POST /dashboard/student-services/counseling/` - Counseling sessions management

### 7. Gestion des bourses
**Description**: Recevoir la liste des boursiers des organismes externes. Mettre à jour le statut financier des étudiants.

**Endpoints**:
- `GET/POST /dashboard/student-services/scholarships/` - Scholarship management

### 8. Gestion des Activités Étudiantes
**Description**: Superviser et enregistrer la création, validation et suivi des clubs et associations étudiantes.

**Endpoints**:
- `GET/POST /dashboard/student-services/activities/` - Student activities management
- `POST /dashboard/student-services/activities/{activity_id}/approve/` - Approve activities

### 9. Mise à Jour du Dossier Étudiant
**Description**: Mettre à jour les informations personnelles et administratives clés de l'étudiant.

**Endpoints**:
- `PUT /dashboard/student-services/students/{student_id}/update/` - Update student profiles

### 10. Aide à la décision
**Description**: Générer des rapports et statistiques sur les effectifs, taux de réussite, données d'inscription.

**Endpoints**:
- `GET /dashboard/student-services/reports/enrollment/` - Enrollment reports
- `GET /dashboard/student-services/population/` - Student population data

## API Endpoints

### Dashboard Overview
```
GET /dashboard/student-services/overview/
```
Returns student services dashboard statistics including pending requests, active scholarships, upcoming sessions.

### Document Management
```
GET /dashboard/student-services/documents/
POST /dashboard/student-services/documents/
```
Manage student document requests (diplomas, certificates, attestations).

```
POST /dashboard/student-services/documents/{request_id}/process/
```
Process document requests. Request body:
```json
{
    "action": "processing|ready|delivered|rejected",
    "notes": "Processing notes"
}
```

### Absence Management
```
GET /dashboard/student-services/absences/
POST /dashboard/student-services/absences/
```
Manage student absence justifications.

```
POST /dashboard/student-services/absences/{absence_id}/process/
```
Process absence justifications. Request body:
```json
{
    "decision": "approved|rejected"
}
```

### Student Activities
```
GET /dashboard/student-services/activities/
POST /dashboard/student-services/activities/
```
Manage student clubs, associations, and events.

```
POST /dashboard/student-services/activities/{activity_id}/approve/
```
Approve student activities and clubs.

### Scholarship Management
```
GET /dashboard/student-services/scholarships/
POST /dashboard/student-services/scholarships/
```
Manage student scholarships and financial aid.

### Counseling Sessions
```
GET /dashboard/student-services/counseling/
POST /dashboard/student-services/counseling/
```
Schedule and manage orientation and counseling sessions.

### Reports & Analytics
```
GET /dashboard/student-services/reports/enrollment/?academic_year=2024
```
Generate enrollment statistics and reports.

```
GET /dashboard/student-services/population/
```
Get student population data by year and class.

### Student Profile Management
```
PUT /dashboard/student-services/students/{student_id}/update/
```
Update student personal and administrative information.

## Models

### DocumentRequest
Manages student document requests (diplomas, certificates, attestations).

### AbsenceJustification
Tracks student absence justifications and approvals.

### StudentActivity
Manages student clubs, associations, and extracurricular activities.

### Scholarship
Tracks student scholarships and financial aid.

### CounselingSession
Manages orientation and counseling sessions.

## Key Features

✅ **Document Processing**: Complete workflow for student document requests
✅ **Absence Management**: Justification tracking and professor notification
✅ **Activity Supervision**: Club and association management
✅ **Scholarship Coordination**: Financial aid tracking and coordination
✅ **Counseling Services**: Orientation and academic counseling sessions
✅ **Profile Management**: Student information updates
✅ **Reporting**: Enrollment statistics and population analytics
✅ **Compliance Control**: Academic and financial conformity verification

## Installation

1. Add `services.dependent_service.dashboard_module.dashboard_student_services_app` to `INSTALLED_APPS`
2. Run migrations: `python manage.py makemigrations dashboard_student_services_app && python manage.py migrate`

## Usage

All endpoints require Student Services authentication.

Example usage:
```python
# Process document request
response = requests.post('/dashboard/student-services/documents/{id}/process/',
                        json={'action': 'ready', 'notes': 'Document prepared'},
                        headers={'Authorization': 'Bearer <token>'})

# Approve student activity
response = requests.post('/dashboard/student-services/activities/{id}/approve/',
                        headers={'Authorization': 'Bearer <token>'})
```

## Role Philosophy

The Student Services dashboard is designed as:
- **Central Administrative Hub**: Single point for all student-related administrative tasks
- **Data Manager**: Comprehensive student information management
- **Compliance Controller**: Academic and financial conformity verification
- **Communication Bridge**: Interface between students, faculty, and administration
