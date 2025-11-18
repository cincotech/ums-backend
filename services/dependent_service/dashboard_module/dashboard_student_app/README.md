# Student Dashboard

Dashboard specifically designed for Students (ÉTUDIANTS) - providing comprehensive access to academic information, administrative services, and communication tools for their university experience.

## Use Cases

### 1. Inscription/Réinscription
**Description**: Compléter les formulaires, payer les frais de scolarité et valider son inscription en ligne.

**Endpoints**:
- Integration with existing enrollment system
- Online form completion and fee payment

### 2. Mise à Jour du Profil
**Description**: Gérer ses informations personnelles (adresse, téléphone, email, etc.) pour s'assurer que l'administration dispose de données exactes.

**Endpoints**:
- `GET/PUT /dashboard/student/profile/` - View and update personal information

### 3. Consultation des Notes
**Description**: Accéder à ses résultats d'examens, de travaux pratiques et de devoirs, en temps réel après correction SOUS CONDITIONS D'AVOIR PAYÉ LA TRANCHE EXIGÉE.

**Endpoints**:
- `GET /dashboard/student/grades/` - View grades (payment-conditional)

### 4. Relevés de Notes et Bulletins
**Description**: Télécharger ou consulter ses relevés de notes officiels, ainsi que le relevé de son parcours UNE FOIS L'ANNÉE CLÔTURÉE.

**Endpoints**:
- `GET /dashboard/student/transcript/` - Official transcripts (year-end only)

### 5. Suivi de la Progression
**Description**: Vérifier l'avancement dans son cursus, les crédits validés (ECTS) et ceux restants pour l'obtention du diplôme.

**Endpoints**:
- `GET /dashboard/student/progress/` - Academic progression and credits tracking

### 6. Emploi du Temps
**Description**: Consulter son horaire de cours mis à jour dynamiquement, y compris les changements de salle ou les annulations.

**Endpoints**:
- `GET /dashboard/student/schedule/` - Dynamic class schedule

### 7. Calendrier Académique
**Description**: Suivre les dates importantes (début et fin de semestre, examens, soutenances, jours fériés, etc.).

**Endpoints**:
- Integration with academic calendar system

### 8. Gestion des Absences
**Description**: Consulter son propre registre d'assiduité (présences/absences) aux cours et aux travaux dirigés.

**Endpoints**:
- `GET /dashboard/student/attendance/` - Personal attendance record

### 9. Messagerie Intégrée
**Description**: Communiquer directement avec les professeurs, les assistants ou l'administration.

**Endpoints**:
- `GET/POST /dashboard/student/messages/` - Internal messaging system

### 10. Plateforme de Cours (LMS/Intégration)
**Description**: L'application sera liée à une plateforme d'apprentissage (LMS) pour télécharger supports, rendre devoirs, accéder aux ressources.

**Endpoints**:
- Future LMS integration endpoints

### 11. Notifications
**Description**: Recevoir des alertes importantes (paiement, changement d'emploi du temps, ouverture des inscriptions, résultats d'examen).

**Endpoints**:
- `GET/POST /dashboard/student/notifications/` - Notification management

### 12. Consultation et Téléchargement Immédiat
**Description**: Accéder directement aux documents générés automatiquement par le système.

**Endpoints**:
- `GET /dashboard/student/downloads/` - Available documents for download

### 13. Demande de Documents Spécifiques
**Description**: Soumettre des requêtes pour des documents nécessitant une intervention humaine ou une signature officielle.

**Endpoints**:
- `GET/POST /dashboard/student/documents/` - Document request management

## API Endpoints

### Dashboard Overview
```
GET /dashboard/student/overview/
```
Returns student dashboard statistics including notifications, GPA, attendance rate, payment status.

### Profile Management
```
GET /dashboard/student/profile/
PUT /dashboard/student/profile/
```
View and update personal information (address, phone, email, etc.).

### Academic Information
```
GET /dashboard/student/grades/
```
Access exam results, practical work, and assignments (payment-conditional).

```
GET /dashboard/student/transcript/
```
Download official transcripts and academic records (year-end only).

```
GET /dashboard/student/progress/
```
Track academic progression, validated credits (ECTS), and remaining requirements.

### Schedule & Attendance
```
GET /dashboard/student/schedule/
```
View dynamically updated class schedule including room changes and cancellations.

```
GET /dashboard/student/attendance/
```
Personal attendance record for courses and tutorials.

### Communication
```
GET /dashboard/student/messages/
POST /dashboard/student/messages/
```
Internal messaging with professors, assistants, and administration.

### Notifications
```
GET /dashboard/student/notifications/
POST /dashboard/student/notifications/
```
Receive and manage important alerts (payments, schedule changes, exam results).

### Document Services
```
GET /dashboard/student/downloads/
```
Access automatically generated documents:
- Current year enrollment certificate
- Last validated semester transcript
- Enrollment or payment attestation
- Personal schedule

```
GET /dashboard/student/documents/
POST /dashboard/student/documents/
```
Request official documents requiring human intervention:
- Student card (loss/renewal)
- Diploma duplicate
- Transfer or departure certificate

## Models

### StudentNotification
Manages important alerts and notifications for students.

### StudentDocumentRequest
Handles requests for official documents requiring processing.

### StudentMessage
Internal messaging system for communication with faculty and administration.

### StudentAttendance
Personal attendance tracking for courses and tutorials.

## Key Features

✅ **Payment-Conditional Access**: Grades accessible only after payment
✅ **Real-Time Updates**: Dynamic schedule and notification system
✅ **Academic Tracking**: Complete progression and credit monitoring
✅ **Document Management**: Both automatic and request-based document access
✅ **Communication Hub**: Direct messaging with professors and administration
✅ **Attendance Monitoring**: Personal attendance record access
✅ **Profile Management**: Self-service personal information updates
✅ **Notification System**: Important alerts and updates
✅ **Year-End Restrictions**: Official transcripts only when year is closed

## Installation

1. Add `services.dependent_service.dashboard_module.dashboard_student_app` to `INSTALLED_APPS`
2. Run migrations: `python manage.py makemigrations dashboard_student_app && python manage.py migrate`

## Usage

All endpoints require Student authentication.

Example usage:
```python
# Update profile
response = requests.put('/dashboard/student/profile/',
                       json={'phone_number': '+123456789', 'email': 'new@email.com'},
                       headers={'Authorization': 'Bearer <token>'})

# Request document
response = requests.post('/dashboard/student/documents/',
                        json={'document_type': 'student_card', 'purpose': 'Lost card replacement'},
                        headers={'Authorization': 'Bearer <token>'})

# Send message
response = requests.post('/dashboard/student/messages/',
                        json={'recipient_id': 'teacher_id', 'subject': 'Question about course', 'content': 'Message content'},
                        headers={'Authorization': 'Bearer <token>'})
```

## Access Conditions

### Payment-Conditional Features:
- **Grade Access**: Requires payment of required installment
- **Transcript Download**: Only available when academic year is closed
- **Document Requests**: May require supporting documents and justifications

### Real-Time Features:
- **Schedule Updates**: Dynamic updates including room changes and cancellations
- **Notifications**: Immediate alerts for important events
- **Attendance Tracking**: Real-time attendance record updates

## Student Experience Philosophy

The Student dashboard is designed to provide:
- **Self-Service Access**: Maximum autonomy for routine academic information
- **Conditional Access**: Appropriate restrictions based on payment and academic status
- **Communication Tools**: Direct channels to faculty and administration
- **Progress Transparency**: Clear visibility into academic advancement
- **Document Efficiency**: Streamlined access to both automatic and requested documents
