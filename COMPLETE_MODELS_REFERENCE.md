# Complete UMS Models Reference Guide

**Project:** University Management System (UMS)
**Date:** 2025-11-17
**Purpose:** Comprehensive reference of ALL models in the UMS project to prevent duplicate model creation

---

## Table of Contents
1. [Foundational Service Models](#foundational-service-models)
2. [Core Service Models](#core-service-models)
3. [Dependent Service Models](#dependent-service-models)
4. [Dashboard Module Models](#dashboard-module-models)
5. [Model Usage Guidelines](#model-usage-guidelines)
6. [Common Mistakes to Avoid](#common-mistakes-to-avoid)

---

## FOUNDATIONAL SERVICE MODELS

### ⚠️ NEVER CREATE DUPLICATES OF THESE MODELS

These are the base models that should be imported and reused throughout the entire project. **DO NOT recreate these in any dashboard or other module.**

### Auth Module

#### 📍 User Model
**Location:** `services.foundational_service.auth_module.user_app.models`

```python
from services.foundational_service.auth_module.user_app.models import User, Role
```

**Models:**
- **User** - Main user model (extends AbstractUser)
  - Fields: email (username), first_name, last_name, phone_number, birth_date, gender, marital_status, nationality (FK to Country), residence (M2M to Colline), role (FK to Role), email_verified, 2FA settings, profile_picture, spoken_languages
  - Use for: ALL user authentication and user references

- **Role** - User roles
  - Fields: name, description
  - Use for: Role-based access control

#### 📍 Profile Models
**Location:** `services.foundational_service.auth_module.authorization_app.models`

```python
from services.foundational_service.auth_module.authorization_app.models import Profile, Supervisor
```

**Models:**
- **Profile** - Staff/admin profiles (combines Dean, Rector, StudentService, FinanceService, etc.)
  - Fields: user (1-to-1 with User), position, room (FK to Room), start_date, end_date, faculty (FK to Faculty), university (FK to University)
  - Use for: Staff member profiles and administrative roles

- **Supervisor** - Exam supervisors
  - Fields: user (1-to-1 with User), is_supervisor_active
  - Use for: Exam supervision assignments

### Geo Module

#### 📍 Geographic Models
**Location:** `services.foundational_service.geo_module.*`

```python
from services.foundational_service.geo_module.country_app.models import Country
from services.foundational_service.geo_module.province_app.models import Province
from services.foundational_service.geo_module.commune_app.models import Commune
from services.foundational_service.geo_module.zone_app.models import Zone
from services.foundational_service.geo_module.colline_app.models import Colline
```

**Models:**
- **Country** - Countries
  - Fields: code, country_name
  - Use for: Nationality, university location

- **Province** - Provinces
  - Fields: province_name, country (FK to Country)
  - Use for: Geographic references

- **Commune** - Communes
  - Fields: commune_name, province (FK to Province)
  - Use for: Geographic references, training centers

- **Zone** - Zones
  - Fields: zone_name, commune (FK to Commune)
  - Use for: Geographic references, highschools

- **Colline** - Collines (smallest geographic unit)
  - Fields: colline_name, zone (FK to Zone)
  - Use for: Student birthplace, user residence

**Geographic Hierarchy:**
```
Country → Province → Commune → Zone → Colline
```

---

## CORE SERVICE MODELS

### ⚠️ THESE ARE CORE BUSINESS MODELS - IMPORT, DON'T RECREATE

### Academic Module

#### 📍 University Structure
**Location:** `services.core_service.academic_module.university_app.models`

```python
from services.core_service.academic_module.university_app.models import (
    University,
    AcademicYear,
    UniversityDegree,
)
```

**Models:**
- **University** - Universities
  - Fields: university_name, university_abrev, country (FK to Country)
  - Use for: University identification

- **AcademicYear** - Academic years
  - Fields: academic_year, description, civil_year, start_date, end_date
  - Use for: Year-based operations, inscriptions, attributions

- **UniversityDegree** - Degree types (Bachelor, Master, PhD, etc.)
  - Fields: degree_name, description
  - Use for: Student degrees, teacher qualifications

#### 📍 Academic Hierarchy
**Locations:** Various apps in `academic_module`

```python
from services.core_service.academic_module.faculty_app.models import Faculty, TypeFormation
from services.core_service.academic_module.department_app.models import Department
from services.core_service.academic_module.class_app.models import Class
from services.core_service.academic_module.module_app.models import Module
from services.core_service.academic_module.course_app.models import Course
```

**Models:**
- **TypeFormation** - Formation types (F, I, M, D codes)
  - Fields: name, code, description
  - Use for: Faculty classification

- **Faculty** - Faculties
  - Fields: faculty_name, faculty_abreviation, types (FK to TypeFormation), university (FK to University)
  - Use for: Faculty references

- **Department** - Departments within faculties
  - Fields: department_name, abreviation, faculty (FK to Faculty)
  - Use for: Department references

- **Class** - Classes/programs
  - Fields: class_name, department (FK to Department), class_group (JSON array)
  - Use for: Student enrollment

- **Module** - Course modules/units
  - Fields: class_fk (FK to Class), module_name, code, semester_id
  - Use for: Course organization

- **Course** - Individual courses
  - Fields: module (FK to Module), course_name, cm, td, tp (hours)
  - Use for: Course references, exams, results, attributions

**Academic Hierarchy:**
```
University → Faculty → Department → Class → Module → Course
```

#### 📍 Teacher Models
**Location:** `services.core_service.academic_module.teacher_app.models`

```python
from services.core_service.academic_module.teacher_app.models import (
    Teacher,
    Attribution,
    Suggestion,
)
```

**Models:**
- **Teacher** - Teacher profiles
  - Fields: user (1-to-1 with User), teacher_grade, degree (FK to UniversityDegree), university (FK to University), speciality, url_cv, url_other, url_diploma
  - Use for: Teacher references

- **Attribution** - Course assignments to teachers
  - Fields: course (FK to Course), principal_teacher (FK to Teacher), substitute_teacher (FK to Teacher), academic_year (FK to AcademicYear), date_attribution, status_principal_teacher, status_substitute_teacher, commentaire, submitted_by (FK to User), authorized_by (FK to User)
  - Use for: Course-teacher assignments

- **Suggestion** - Attribution suggestions
  - Fields: suggestion_date, suggestion, attribution (FK to Attribution), teacher (FK to Teacher), user (FK to User)
  - Use for: Teacher suggestions for attributions

### Student Module

#### 📍 Student Core Models
**Location:** `services.core_service.student_module.student_profile_app.models`

```python
from services.core_service.student_module.student_profile_app.models import (
    Student,
    Training,
    StudentHsInfo,
    StudentGraduateInfo,
)
```

**Models:**
- **Student** - Student profiles (⭐ MOST IMPORTANT)
  - Fields: user (1-to-1 with User), matricule, colline (FK to Colline - birthplace), cam, parent (M2M to Parent)
  - Use for: ALL student references, the core student model

- **Training** - Professional training
  - Fields: domaine, certificate, training_center (FK to TrainingCenter)
  - Use for: Vocational training records

- **StudentHsInfo** - High school information
  - Fields: student (FK to Student), highschool (FK to Highschool), certificate (FK to Certificate), se_mark, date_of_obtention, formation (M2M to Training)
  - Use for: Student high school background

- **StudentGraduateInfo** - University background
  - Fields: student (FK to Student), department (FK to Department), option, mention, degree (FK to UniversityDegree)
  - Use for: Previous university education

#### 📍 Parent Models
**Location:** `services.core_service.student_module.parent_app.models`

```python
from services.core_service.student_module.parent_app.models import Parent, Profession
```

**Models:**
- **Parent** - Student parents/guardians
  - Fields: parent_name, parent_phone, parent_email, profession (FK to Profession), parent_type (F/M/G), is_alive, is_contact_person
  - Use for: Parent/guardian information

- **Profession** - Professions
  - Fields: profession_name
  - Use for: Parent professions

#### 📍 High School Models
**Location:** `services.core_service.student_module.highschool_info_app.models`

```python
from services.core_service.student_module.highschool_info_app.models import (
    Highschool,
    Section,
    Certificate,
    Option,
    TrainingCenter,
)
```

**Models:**
- **Highschool** - High schools
  - Fields: hs_name, zone (FK to Zone), code

- **Section** - Academic sections
  - Fields: section_name

- **Certificate** - Certificate types
  - Fields: certificate_name, section (FK to Section)

- **Option** - Academic options
  - Fields: option_name, section (FK to Section)

- **TrainingCenter** - Vocational training centers
  - Fields: name, commune (FK to Commune)

#### 📍 Inscription Model
**Location:** `services.core_service.student_module.inscription_app.models`

```python
from services.core_service.student_module.inscription_app.models import Inscription
```

**Models:**
- **Inscription** - Student enrollment (⭐ CRITICAL MODEL)
  - Fields: student (FK to Student), academic_year (FK to AcademicYear), class_fk (FK to Class), date_inscription, regist_status, groupe, withdrawal_date, is_year_close
  - Use for: Student enrollment records, linking students to classes/years
  - ⚠️ **Many models reference this instead of Student directly**

#### 📍 Student Card Models
**Location:** `services.core_service.student_module.card_app.models`

```python
from services.core_service.student_module.card_app.models import StudentCard, StudentCardLog
```

**Models:**
- **StudentCard** - Student ID cards
  - Fields: student (FK to Student), card_number, issue_date, expiry_date, status, printed_by (FK to User), photo, qrcode_data
  - Use for: Student ID card management

- **StudentCardLog** - Card action history
  - Fields: card (FK to StudentCard), action, action_date, performed_by, remarks
  - Use for: Card lifecycle tracking

### Finance Module

#### 📍 Fees Models
**Location:** `services.core_service.finance_module.fees_app.models`

```python
from services.core_service.finance_module.fees_app.models import FeesSheet, Wording
```

**Models:**
- **FeesSheet** - Fee structures
  - Fields: class_fk (FK to Class), academic_year (FK to AcademicYear), wording (FK to Wording), base_amount, installements (JSON)
  - Use for: Fee definitions per class/year

- **Wording** - Fee descriptions
  - Fields: wording_name
  - Use for: Fee type descriptions

#### 📍 Payment Models
**Location:** `services.core_service.finance_module.payment_app.models`

```python
from services.core_service.finance_module.payment_app.models import Payment, Bank
```

**Models:**
- **Payment** - Payment records (⭐ IMPORTANT)
  - Fields: feessheet (FK to FeesSheet), amount_paid, payment_date, reception_date, payment_method, bank (FK to Bank), bank_slip_ref, transaction_code, inscription (FK to Inscription), user (FK to User), description, remittance_slip_uri, payment_status
  - Use for: ALL payment tracking
  - ⚠️ **DO NOT create custom payment models in dashboards**

- **Bank** - Bank information
  - Fields: bank_name, bank_abreviation
  - Use for: Bank references

#### 📍 Debt Cancellation
**Location:** `services.core_service.finance_module.concellation_app.models`

```python
from services.core_service.finance_module.concellation_app.models import DebtCancellation
```

**Models:**
- **DebtCancellation** - Debt forgiveness
  - Fields: inscription (FK to Inscription), feessheet (FK to FeesSheet), cancelation_date, cancelled_amount, reason
  - Use for: Debt cancellation tracking

---

## DEPENDENT SERVICE MODELS

### Exam Module

#### 📍 Exam Models
**Location:** `services.dependent_service.exam_module.exam_app.models`

```python
from services.dependent_service.exam_module.exam_app.models import (
    Exam,
    ExamType,
    ExamRoom,
    ExamSupervisor,
)
```

**Models:**
- **ExamType** - Types of exams
  - Fields: exam_type_name, description

- **Exam** - Exam scheduling
  - Fields: course (FK to Course), exam_type (FK to ExamType), academic_year (FK to AcademicYear), exam_date, start_time, end_time, status
  - Use for: Exam scheduling

- **ExamRoom** - Room assignments for exams
  - Fields: exam (FK to Exam), room (FK to Room), range_student

- **ExamSupervisor** - Supervisor assignments
  - Fields: exam_room (FK to ExamRoom), supervisor (FK to Supervisor)

#### 📍 Result Models
**Location:** `services.dependent_service.exam_module.result_app.models`

```python
from services.dependent_service.exam_module.result_app.models import (
    Result,
    CompiledResult,
    Session,
    Supplement,
)
```

**Models:**
- **Session** - Exam sessions
  - Fields: session_name

- **Result** - Individual exam results (⭐ IMPORTANT)
  - Fields: course (FK to Course), inscription (FK to Inscription), session (FK to Session), mark
  - Use for: Individual course grades

- **CompiledResult** - Compiled academic results
  - Fields: results (JSON), inscription (FK to Inscription), average_mark, status, is_promoted
  - Use for: Semester/year results

- **Supplement** - Supplementary exams
  - Fields: inscription (FK to Inscription), course (FK to Course), validation, validation_date, mark

#### 📍 Exam Attendance
**Location:** `services.dependent_service.exam_module.attendance_app.models`

```python
from services.dependent_service.exam_module.attendance_app.models import ExamAttendance
```

**Models:**
- **ExamAttendance** - Exam attendance tracking
  - Fields: examroom (FK to ExamRoom), card (FK to StudentCard), inscription (FK to Inscription), attendance_time, status
  - Use for: Tracking exam attendance
  - ⚠️ **Different from class Attendance in scheduling module**

### Document Module

#### 📍 Document Models
**Location:** `services.dependent_service.document_module.*`

```python
from services.dependent_service.document_module.document_app.models import Document
from services.dependent_service.document_module.request_app.models import Request
```

**Models:**
- **Document** - Document types
  - Fields: document_name, document_description, document_price, processing_time
  - Use for: Available document types (certificates, transcripts, etc.)

- **Request** - Document requests (⭐ IMPORTANT)
  - Fields: student (FK to Student), document (FK to Document), request_date, request_status, payment_verified, admin_comment, updated_at, payment (FK to Payment)
  - Use for: Student document requests
  - ⚠️ **DO NOT create DocumentRequest models in dashboards - use this!**

### Infrastructure Module

#### 📍 Building & Room Models
**Locations:** `services.dependent_service.infrastructure_module.*`

```python
from services.dependent_service.infrastructure_module.building_app.models import Building
from services.dependent_service.infrastructure_module.room_app.models import Room
```

**Models:**
- **Building** - Buildings
  - Fields: university (FK to University), building_name, building_code, location

- **Room** - Rooms (⭐ IMPORTANT)
  - Fields: building (FK to Building), room_name, capacity, room_type (classroom/laboratory/amphi/office/meeting), is_available
  - Use for: ALL room references (classrooms, offices, etc.)

#### 📍 Equipment Models
**Location:** `services.dependent_service.infrastructure_module.equipment_app.models`

```python
from services.dependent_service.infrastructure_module.equipment_app.models import (
    Equipment,
    EquipmentType,
    EquipmentAllocation,
    EquipmentMaintenance,
)
```

**Models:**
- **EquipmentType** - Equipment categories
  - Fields: name

- **Equipment** - Equipment inventory
  - Fields: equipment_name, equipment_type (FK to EquipmentType), serial_number, equipment_number, purchase_date, status

- **EquipmentAllocation** - Equipment assignments
  - Fields: equipment (FK to Equipment), room (FK to Room), allocated_to (FK to User), allocation_date, return_date, status

- **EquipmentMaintenance** - Maintenance records
  - Fields: equipment (FK to Equipment), maintenance_date, return_date, description, performed_by, cost

### Scheduling Module

#### 📍 Scheduling Models
**Location:** `services.dependent_service.scheduling_module.scheduling_app.models`

```python
from services.dependent_service.scheduling_module.scheduling_app.models import (
    ScheduleSlot,
    Timetable,
    Attendance,
    ActivityReport,
)
```

**Models:**
- **ScheduleSlot** - Time slots
  - Fields: day_of_week, start_time, end_time, schedule_name

- **Timetable** - Class schedules
  - Fields: attribution (FK to Attribution), room (FK to Room), slot (M2M to ScheduleSlot), start_date, end_date, status

- **Attendance** - Class attendance (⭐ IMPORTANT)
  - Fields: timetable (FK to Timetable), student (FK to Student), status, remarks
  - Use for: Regular class attendance tracking
  - ⚠️ **DO NOT create StudentAttendance models - use this!**

- **ActivityReport** - Teaching activity reports
  - Fields: timetable (FK to Timetable), planned_hours, delivered_hours, completion_rate, observations

### Notification Module

#### 📍 Event Notification
**Location:** `services.dependent_service.notification_module.event_notification_app.models`

*Note: Models exist but were not read in detail. Check the file for specific models.*

---

## DASHBOARD MODULE MODELS

### ⚠️ ONLY DASHBOARD-SPECIFIC MODELS HERE

### Shared Dashboard Models

#### 📍 Shared Models (Centralized)
**Location:** `services.dependent_service.dashboard_module.dashboard_shared_app.models`

```python
from services.dependent_service.dashboard_module.dashboard_shared_app.models import (
    Notification,
    Message,
    AuditLog,
    SystemConfiguration,
    BackupRecord,
)
```

**Models (APPROVED - Dashboard-specific):**
- **Notification** - Unified notification system
  - Fields: recipient (FK to User), recipient_type, notification_type, title, message, is_read, created_at
  - Use for: All dashboard notifications

- **Message** - Unified messaging system
  - Fields: sender (FK to User), recipient (FK to User), message_type, subject, content, is_read, sent_at
  - Use for: Internal messaging

- **AuditLog** - System audit logging
  - Fields: user (FK to User), action, model_name, object_id, changes (JSON), ip_address, timestamp
  - Use for: Activity tracking

- **SystemConfiguration** - Global configuration
  - Fields: config_type, key, value (JSON), is_active, created_by (FK to User), created_at, updated_at
  - Use for: System settings

- **BackupRecord** - Backup management
  - Fields: backup_type, status, file_path, file_size, initiated_by (FK to User), started_at, completed_at, error_message
  - Use for: Backup tracking

### Dashboard-Specific Models

#### 📍 Base Dashboard
**Location:** `services.dependent_service.dashboard_module.dashboard_app.models`

```python
from services.dependent_service.dashboard_module.dashboard_app.models import (
    QualityReport,
    AttributionValidation,
)
```

**Models:**
- **QualityReport** - Quality reports
- **AttributionValidation** - Attribution validation tracking

#### 📍 Recteur Dashboard
**Location:** `services.dependent_service.dashboard_module.dashboard_recteur_app.models`

```python
from services.dependent_service.dashboard_module.dashboard_recteur_app.models import (
    PaymentDerogation,
    RecteurDecision,
)
```

**Models:**
- **PaymentDerogation** - Payment exceptions/deferrals
- **RecteurDecision** - High-level administrative decisions

#### 📍 Quality Director Dashboard
**Location:** `services.dependent_service.dashboard_module.dashboard_quality_director_app.models`

```python
from services.dependent_service.dashboard_module.dashboard_quality_director_app.models import (
    StudentSurvey,
    QualityStandard,
    ComplianceAudit,
)
```

**Models:**
- **StudentSurvey** - Student evaluations
- **QualityStandard** - Quality standards
- **ComplianceAudit** - Audit records

#### 📍 Academic Secretary Dashboard
**Location:** `services.dependent_service.dashboard_module.dashboard_academic_secretary_app.models`

```python
from services.dependent_service.dashboard_module.dashboard_academic_secretary_app.models import (
    ExamSession,
    ExamAttendance,
    JurySession,
    JuryDecision,
    GradeComplaint,
    OfficialDocument,
    TeacherPaymentClaim,
)
```

**Models:**
- **ExamSession** - Jury exam sessions (may overlap with exam module)
- **ExamAttendance** - May be duplicate of exam module
- **JurySession** - Jury deliberation sessions
- **JuryDecision** - Jury decisions on students
- **GradeComplaint** - Grade appeals
- **OfficialDocument** - Official document management
- **TeacherPaymentClaim** - Teacher payment claims

⚠️ **POTENTIAL ISSUES:**
- `ExamSession` and `ExamAttendance` may duplicate functionality from `exam_module`
- Review if these should reference existing models instead

#### 📍 Student Services Dashboard
**Location:** `services.dependent_service.dashboard_module.dashboard_student_services_app.models`

```python
from services.dependent_service.dashboard_module.dashboard_student_services_app.models import (
    DocumentRequest,
    AbsenceJustification,
    StudentActivity,
    Scholarship,
    CounselingSession,
)
```

**Models:**
- **DocumentRequest** - ⚠️ POTENTIAL DUPLICATE
- **AbsenceJustification** - Absence justifications
- **StudentActivity** - Student activities/clubs
- **Scholarship** - Scholarship management
- **CounselingSession** - Counseling sessions

⚠️ **ISSUE IDENTIFIED:**
- `DocumentRequest` may be a duplicate of `Request` model in `document_module`
- **Recommendation:** Review if this should use the core `Request` model

#### 📍 Collection Agent Dashboard
**Location:** `services.dependent_service.dashboard_module.dashboard_collection_agent_app.models`

```python
from services.dependent_service.dashboard_module.dashboard_collection_agent_app.models import (
    PaymentInstallment,
    PaymentReminder,
    PaymentPlan,
    PaymentPromise,
    CollectionCorrespondence,
    LegalCase,
)
```

**Models:**
- **PaymentInstallment** - Payment plan installments (may relate to FeesSheet.installements)
- **PaymentReminder** - Payment reminders
- **PaymentPlan** - Payment plans
- **PaymentPromise** - Payment promises
- **CollectionCorrespondence** - Collection communications
- **LegalCase** - Legal cases for debt collection

#### 📍 Alumni Dashboard
**Location:** `services.dependent_service.dashboard_module.dashboard_alumni_app.models`

```python
from services.dependent_service.dashboard_module.dashboard_alumni_app.models import (
    AlumniProfile,
    JobOffer,
    MentorshipProgram,
    AlumniTestimonial,
    AlumniEvent,
    AlumniEventRegistration,
    AlumniDonation,
)
```

**Models:**
- **AlumniProfile** - Alumni profiles
- **JobOffer** - Job postings
- **MentorshipProgram** - Mentorship programs
- **AlumniTestimonial** - Testimonials
- **AlumniEvent** - Alumni events
- **AlumniEventRegistration** - Event registrations
- **AlumniDonation** - Donations

---

## MODEL USAGE GUIDELINES

### Rule #1: NEVER Recreate Foundational Models

**❌ NEVER CREATE:**
- User models
- Geographic models (Country, Province, Commune, Zone, Colline)
- Role models

**✅ ALWAYS IMPORT:**
```python
from services.foundational_service.auth_module.user_app.models import User, Role
from services.foundational_service.geo_module.country_app.models import Country
# etc.
```

### Rule #2: NEVER Recreate Core Business Models

**❌ NEVER CREATE:**
- Student models
- Teacher models
- Course/Class/Module models
- Payment models
- Inscription models

**✅ ALWAYS IMPORT:**
```python
from services.core_service.student_module.student_profile_app.models import Student
from services.core_service.academic_module.teacher_app.models import Teacher
from services.core_service.finance_module.payment_app.models import Payment
from services.core_service.student_module.inscription_app.models import Inscription
```

### Rule #3: Check Dependent Services Before Creating

Before creating a new model in a dashboard, check if it exists in:
1. **exam_module** - for exam-related models
2. **document_module** - for document-related models
3. **scheduling_module** - for attendance and timetable models
4. **infrastructure_module** - for room and equipment models

**Example - Document Requests:**
```python
# ❌ WRONG - Creating duplicate
class StudentDocumentRequest(models.Model):
    student = models.ForeignKey(Student, on_delete=models.CASCADE)
    document_type = models.CharField(...)
    # ...

# ✅ CORRECT - Using existing model
from services.dependent_service.document_module.request_app.models import Request

# Use Request model instead
```

### Rule #4: When to Create Dashboard Models

Create dashboard-specific models ONLY for:
1. **Dashboard-specific functionality** (e.g., QualityReport, AttributionValidation)
2. **Notifications and messaging** (centralized in dashboard_shared_app)
3. **Dashboard-specific workflows** (e.g., JuryDecision, PaymentDerogation)
4. **UI state/preferences** (if needed)

**DO NOT create dashboard models for:**
- Core business entities (students, teachers, courses, etc.)
- Transactions (payments, enrollment, etc.)
- Documents or requests
- Attendance tracking
- Exam results

### Rule #5: Reference via Inscription When Appropriate

Many models reference `Inscription` instead of `Student` directly because:
- Inscription links Student + AcademicYear + Class
- Provides context for year-specific operations
- Prevents ambiguity (which year? which class?)

**Example:**
```python
# ✅ GOOD - References inscription
class Result(models.Model):
    inscription = models.ForeignKey(Inscription, on_delete=models.RESTRICT)
    course = models.ForeignKey(Course, on_delete=models.RESTRICT)
    mark = models.FloatField()

# ❌ LESS IDEAL - Direct student reference loses context
class Result(models.Model):
    student = models.ForeignKey(Student, on_delete=models.RESTRICT)  # Which year?
    course = models.ForeignKey(Course, on_delete=models.RESTRICT)
    mark = models.FloatField()
```

---

## COMMON MISTAKES TO AVOID

### Mistake #1: Creating StudentNotification/StudentMessage

**❌ WRONG:**
```python
# In dashboard_student_app/models.py
class StudentNotification(models.Model):
    student = models.ForeignKey(Student, on_delete=models.CASCADE)
    notification_type = models.CharField(...)
    # ...
```

**✅ CORRECT:**
```python
# Use the shared Notification model
from services.dependent_service.dashboard_module.dashboard_shared_app.models import Notification

# Filter by recipient
notifications = Notification.objects.filter(recipient=student.user, recipient_type='student')
```

### Mistake #2: Creating DocumentRequest in Multiple Places

**❌ WRONG:**
```python
# In dashboard_student_app/models.py
class StudentDocumentRequest(models.Model):
    # ...

# In dashboard_student_services_app/models.py
class DocumentRequest(models.Model):
    # ...
```

**✅ CORRECT:**
```python
# Use the core Request model
from services.dependent_service.document_module.request_app.models import Request

# All document requests go through this model
```

### Mistake #3: Creating StudentAttendance

**❌ WRONG:**
```python
# In dashboard_student_app/models.py
class StudentAttendance(models.Model):
    student = models.ForeignKey(Student, on_delete=models.CASCADE)
    course = models.ForeignKey(Course, on_delete=models.CASCADE)
    date = models.DateField()
    # ...
```

**✅ CORRECT:**
```python
# Use existing Attendance model
from services.dependent_service.scheduling_module.scheduling_app.models import Attendance

# Query via inscription
attendance_records = Attendance.objects.filter(
    student=student
).order_by('-timetable__start_date')
```

### Mistake #4: Creating Custom Payment Models

**❌ WRONG:**
```python
# In dashboard_collection_agent_app/models.py
class CustomPayment(models.Model):
    student = models.ForeignKey(Student, on_delete=models.CASCADE)
    amount = models.DecimalField(...)
    # ...
```

**✅ CORRECT:**
```python
# Use the core Payment model
from services.core_service.finance_module.payment_app.models import Payment

# All payments go through this model
```

### Mistake #5: Not Using Existing Relationships

**❌ WRONG:**
```python
# Storing user details redundantly
class DashboardProfile(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    first_name = models.CharField(...)  # Already in User!
    last_name = models.CharField(...)   # Already in User!
    email = models.EmailField(...)      # Already in User!
```

**✅ CORRECT:**
```python
# Use relationships, don't duplicate
# Access via user.first_name, user.last_name, user.email
# Only store dashboard-specific data
class DashboardPreferences(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    theme = models.CharField(...)  # Dashboard-specific
    layout = models.CharField(...)  # Dashboard-specific
```

---

## QUICK REFERENCE: What to Import

### For User Operations
```python
from services.foundational_service.auth_module.user_app.models import User, Role
```

### For Student Operations
```python
from services.core_service.student_module.student_profile_app.models import Student
from services.core_service.student_module.inscription_app.models import Inscription
```

### For Academic Operations
```python
from services.core_service.academic_module.course_app.models import Course
from services.core_service.academic_module.class_app.models import Class
from services.core_service.academic_module.teacher_app.models import Teacher, Attribution
from services.core_service.academic_module.university_app.models import AcademicYear
```

### For Finance Operations
```python
from services.core_service.finance_module.payment_app.models import Payment, Bank
from services.core_service.finance_module.fees_app.models import FeesSheet, Wording
```

### For Document Operations
```python
from services.dependent_service.document_module.document_app.models import Document
from services.dependent_service.document_module.request_app.models import Request
```

### For Exam Operations
```python
from services.dependent_service.exam_module.exam_app.models import Exam, ExamType
from services.dependent_service.exam_module.result_app.models import Result, CompiledResult
from services.dependent_service.exam_module.attendance_app.models import ExamAttendance
```

### For Scheduling Operations
```python
from services.dependent_service.scheduling_module.scheduling_app.models import (
    Timetable,
    Attendance,
    ScheduleSlot,
)
```

### For Infrastructure Operations
```python
from services.dependent_service.infrastructure_module.room_app.models import Room
from services.dependent_service.infrastructure_module.building_app.models import Building
```

### For Dashboard Operations
```python
from services.dependent_service.dashboard_module.dashboard_shared_app.models import (
    Notification,
    Message,
    AuditLog,
    SystemConfiguration,
)
```

---

## CONCLUSION

**Key Principles:**
1. ✅ **Import, don't recreate** - Check existing models first
2. ✅ **Use core models** - They're designed for reuse
3. ✅ **Centralize shared logic** - dashboard_shared_app for common dashboard needs
4. ✅ **Follow relationships** - Use ForeignKey to existing models
5. ✅ **Document-specific only** - Create dashboard models only for dashboard-specific needs

**Before Creating a New Model, Ask:**
1. Does this model exist in foundational_service? → **Import it**
2. Does this model exist in core_service? → **Import it**
3. Does this model exist in dependent_service? → **Import it**
4. Is this truly dashboard-specific functionality? → **Only then create it**

---

**Generated by:** Claude Code AI Assistant
**Date:** 2025-11-17
**Purpose:** Prevent model duplication and improve code quality
