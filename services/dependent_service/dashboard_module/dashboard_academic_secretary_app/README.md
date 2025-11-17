# Academic Secretary Dashboard

Dashboard specifically designed for Academic Secretaries (SECRÉTAIRES ACADÉMIQUES) - the central academic content and process administrators who ensure liaison and coordination between management, teachers, and students while guaranteeing compliance and proper organization of studies.

## Use Cases

### 1. Organisation des Examens
**Description**: Planifier le calendrier des épreuves (dates, heures, durées). Attribuer les surveillants et les salles d'examen. Générer les convocations individuelles pour les étudiants.

**Endpoints**:
- `GET/POST /dashboard/academic-secretary/exams/` - Exam session management
- `POST /dashboard/academic-secretary/exams/{exam_id}/attendance/` - Record exam attendance

### 2. Coordination des Notes
**Description**: Contrôler la saisie des notes par les enseignants. Appliquer les règles de calcul des moyennes et des validations. Gérer les compensations.

**Endpoints**:
- `GET /dashboard/academic-secretary/grades/status/` - Monitor grade entry completion

### 3. Préparation des Jurys
**Description**: Générer les documents de synthèse (procès-verbaux) pour la délibération des résultats. Enregistrer et valider les décisions finales du Jury.

**Endpoints**:
- `GET/POST /dashboard/academic-secretary/juries/` - Jury session management
- `POST /dashboard/academic-secretary/juries/{jury_id}/decisions/` - Record jury decisions

### 4. Rédaction et Communication
**Description**: Utiliser l'outil pour rédiger des notes de service, des circulaires ou des communications officielles pour les étudiants et les enseignants.

**Endpoints**:
- `GET/POST /dashboard/academic-secretary/documents/` - Official document management
- `POST /dashboard/academic-secretary/documents/{document_id}/sign/` - Document signing

### 5. Conseil Réglementaire
**Description**: Gérer et archiver les documents académiques importants. Servir de référence interne pour l'application des règlements académiques.

**Endpoints**:
- Document archival and regulatory compliance management

### 6. Gestion des Examens et de la Logistique
**Description**: Planifier les affectations des surveillants. Gérer les listes d'émargement des étudiants. Enregistrer les incidents d'examen.

**Endpoints**:
- Integrated with exam session management for logistics

### 7. Consultation des Copies et des Réclamations
**Description**: Planifier des créneaux de consultation des copies d'examen. Gérer les demandes de consultation faites par les étudiants.

**Endpoints**:
- `GET /dashboard/academic-secretary/complaints/` - Grade complaint management
- `POST /dashboard/academic-secretary/complaints/{complaint_id}/assign/` - Assign complaints
- `POST /dashboard/academic-secretary/complaints/{complaint_id}/resolve/` - Resolve complaints

### 8. Gestion des Réclamations
**Description**: Recevoir et enregistrer les requêtes de réclamation ou de révision de notes. Attribuer la réclamation à l'enseignant responsable.

**Endpoints**:
- Complete complaint workflow management

### 9. Formalisation et Circulation des Documents Officiels
**Description**: Utiliser les flux de travail électroniques pour faire circuler les documents critiques. Édition de documents. Archivage sécurisé.

**Endpoints**:
- Electronic workflow and document circulation system

### 10. Saisie des Déclarations de Créances
**Description**: Vérifier la conformité de la déclaration de créance avec les tarifs horaires. Valider et faire signer les déclarations. Transmettre au Service Financier.

**Endpoints**:
- `GET /dashboard/academic-secretary/claims/` - Payment claim management
- `POST /dashboard/academic-secretary/claims/{claim_id}/verify/` - Verify claims
- `POST /dashboard/academic-secretary/claims/{claim_id}/approve/` - Approve claims
- `POST /dashboard/academic-secretary/claims/{claim_id}/send-finance/` - Send to finance

## API Endpoints

### Dashboard Overview
```
GET /dashboard/academic-secretary/overview/
```
Returns academic secretary dashboard statistics including pending exams, complaints, documents, and claims.

### Exam Management
```
GET /dashboard/academic-secretary/exams/
POST /dashboard/academic-secretary/exams/
```
Schedule and manage exam sessions with dates, supervisors, and rooms.

```
POST /dashboard/academic-secretary/exams/{exam_id}/attendance/
```
Record student exam attendance and incidents. Request body:
```json
{
    "student_id": "uuid",
    "status": "present|absent|late|incident",
    "incident_notes": "Optional incident description"
}
```

### Grade Coordination
```
GET /dashboard/academic-secretary/grades/status/
```
Monitor grade entry completion status by teachers, including deadlines and completion rates.

### Jury Management
```
GET /dashboard/academic-secretary/juries/
POST /dashboard/academic-secretary/juries/
```
Create and manage jury sessions for deliberations.

```
POST /dashboard/academic-secretary/juries/{jury_id}/decisions/
```
Record jury decisions for students. Request body:
```json
{
    "student_id": "uuid",
    "decision": "admitted|deferred|repeat|excluded",
    "notes": "Decision notes"
}
```

### Complaint Management
```
GET /dashboard/academic-secretary/complaints/
```
View all grade complaints and their status.

```
POST /dashboard/academic-secretary/complaints/{complaint_id}/assign/
```
Assign complaint to teacher or department head.

```
POST /dashboard/academic-secretary/complaints/{complaint_id}/resolve/
```
Resolve complaint with new grade if applicable.

### Document Management
```
GET /dashboard/academic-secretary/documents/
POST /dashboard/academic-secretary/documents/
```
Create and manage official documents (circulars, service notes, minutes).

```
POST /dashboard/academic-secretary/documents/{document_id}/sign/
```
Electronic document signing workflow.

### Payment Claims
```
GET /dashboard/academic-secretary/claims/
```
View teacher payment claims for verification.

```
POST /dashboard/academic-secretary/claims/{claim_id}/verify/
```
Verify claim compliance with hourly rates.

```
POST /dashboard/academic-secretary/claims/{claim_id}/approve/
```
Approve verified claims.

```
POST /dashboard/academic-secretary/claims/{claim_id}/send-finance/
```
Send approved claims to financial service.

## Models

### ExamSession
Manages exam scheduling, supervisors, and logistics.

### ExamAttendance
Records student exam attendance and incidents.

### JurySession
Manages jury deliberation sessions and members.

### JuryDecision
Records final jury decisions for students.

### GradeComplaint
Handles grade complaint workflow and resolution.

### OfficialDocument
Manages official document creation, signing, and archival.

### TeacherPaymentClaim
Processes teacher payment claims and verification.

## Key Features

✅ **Exam Organization**: Complete exam scheduling and logistics management
✅ **Grade Coordination**: Teacher grade entry monitoring and validation
✅ **Jury Management**: Deliberation session organization and decision recording
✅ **Document Workflow**: Official document creation, circulation, and signing
✅ **Complaint Resolution**: Grade complaint assignment and resolution process
✅ **Payment Processing**: Teacher payment claim verification and approval
✅ **Regulatory Compliance**: Academic regulation enforcement and archival
✅ **Communication Tools**: Official correspondence and circular management

## Installation

1. Add `services.dependent_service.dashboard_module.dashboard_academic_secretary_app` to `INSTALLED_APPS`
2. Run migrations: `python manage.py makemigrations dashboard_academic_secretary_app && python manage.py migrate`

## Usage

All endpoints require Academic Secretary authentication.

Example usage:
```python
# Schedule exam
response = requests.post('/dashboard/academic-secretary/exams/',
                        json={'course_id': 'uuid', 'exam_date': '2024-06-15T09:00:00Z', 'duration_minutes': 120, 'room': 'A101'},
                        headers={'Authorization': 'Bearer <token>'})

# Record jury decision
response = requests.post('/dashboard/academic-secretary/juries/{jury_id}/decisions/',
                        json={'student_id': 'uuid', 'decision': 'admitted', 'notes': 'Excellent performance'},
                        headers={'Authorization': 'Bearer <token>'})

# Verify payment claim
response = requests.post('/dashboard/academic-secretary/claims/{claim_id}/verify/',
                        headers={'Authorization': 'Bearer <token>'})
```

## Academic Secretary Philosophy

The Academic Secretary dashboard is designed as:
- **Central Coordinator**: Bridge between management, teachers, and students
- **Process Guardian**: Ensures academic regulation compliance
- **Document Manager**: Official correspondence and archival system
- **Quality Controller**: Monitors grade entry and academic standards
- **Administrative Hub**: Centralizes all academic administrative processes
