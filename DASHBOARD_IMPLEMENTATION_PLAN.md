# Dashboard Implementation Plan - UMS

**Date:** 2025-11-17
**Purpose:** Implementation plan for all 10 dashboard roles based on functional requirements

---

## Table of Contents
1. [Requirements Analysis](#requirements-analysis)
2. [Mapping to Existing Models](#mapping-to-existing-models)
3. [Missing Models/Features](#missing-modelsfeatures)
4. [Implementation Priority](#implementation-priority)
5. [Detailed Implementation by Role](#detailed-implementation-by-role)

---

## Requirements Analysis

### 1. SUPER ADMINISTRATEUR (Super Admin)

**Dashboard Module:** `dashboard_super_admin_app`

**Use Cases:**
- ✅ User Management - Create, modify, activate/deactivate, delete users
- ✅ Admin Management - Manage admin roles
- ✅ System Configuration - Global settings (academic years, fee types, security)
- ✅ Security & Emergency - Password reset, MFA management
- ⚠️ Program Management - Create, modify programs (should delegate to academic module)
- ✅ Audit & Logging - View activity logs
- ✅ Backup/Restore - Trigger and manage backups

**Existing Models:**
- ✅ User, Role (foundational_service)
- ✅ AuditLog, SystemConfiguration, BackupRecord (dashboard_shared_app)

**Missing Features:**
- Emergency password reset workflow
- MFA management interface
- Backup trigger mechanism

---

### 2. RECTEUR (Rector)

**Dashboard Module:** `dashboard_recteur_app`

**Use Cases:**
- ✅ Payment Derogations - Grant exceptions for payment
- ✅ Course Attribution Validation (Visiting Professors)
- ✅ Global Payment Monitoring - View payment statistics
- ✅ Academic Performance Supervision - View success/retention rates
- ✅ Quality Reports Consultation

**Existing Models:**
- ✅ PaymentDerogation (dashboard_recteur_app)
- ✅ RecteurDecision (dashboard_recteur_app)
- ✅ Attribution (academic_module)
- ✅ Payment (finance_module)
- ✅ Result, CompiledResult (exam_module)
- ✅ QualityReport (dashboard_app)

**Missing Features:**
- Payment statistics dashboard
- Academic performance aggregation views
- Workflow for derogation requests

---

### 3. DIRECTEUR ACADEMIQUE (Academic Director)

**Dashboard Module:** `dashboard_recteur_app` (can share with Recteur)

**Use Cases:**
- ✅ Course Attribution Validation (by Rector's order)
- ✅ Academic Performance Supervision
- ✅ Quality Reports Consultation

**Note:** Similar to Recteur but with delegated authority

---

### 4. DIRECTEUR ASSURANCE QUALITÉ (Quality Assurance Director)

**Dashboard Module:** `dashboard_quality_director_app`

**Use Cases:**
- ✅ Academic Performance Analysis - Aggregate results by course/program/class
- ✅ Program Execution Tracking - Monitor course progress
- ✅ Enrollment & Retention Audit - Statistics on enrolled students
- ✅ Course & Teacher Evaluation - Manage student surveys
- ✅ Standards & Accreditation Tracking - Compliance audits
- ✅ Quality Report Generation

**Existing Models:**
- ✅ StudentSurvey (dashboard_quality_director_app)
- ✅ QualityStandard (dashboard_quality_director_app)
- ✅ ComplianceAudit (dashboard_quality_director_app)
- ✅ Result, CompiledResult (exam_module)
- ✅ Inscription (student_module)
- ✅ ActivityReport (scheduling_module)

**Missing Features:**
- Survey management system
- Accreditation tracking workflow
- Performance analytics aggregation

---

### 5. DOYEN (Dean)

**Dashboard Module:** `dashboard_app` (needs expansion)

**Use Cases:**
- ✅ Schedule Planning & Creation - Create weekly timetables
- ✅ Teaching Progress Monitoring - View activity reports
- ✅ Teacher Management - Course attributions
- ✅ Student Affairs Supervision - View academic results
- ✅ Room Logistics Coordination - Manage room allocations
- ✅ Academic Secretary Communication
- ✅ Program & Curriculum Management - Create/update programs
- ✅ Group Structuring - Assign students to groups

**Existing Models:**
- ✅ Timetable, ScheduleSlot (scheduling_module)
- ✅ Attribution (academic_module)
- ✅ Room (infrastructure_module)
- ✅ Class, Module, Course (academic_module)
- ✅ Inscription (student_module)
- ✅ ActivityReport (scheduling_module)

**Missing Features:**
- Dean-specific dashboard views
- Group assignment interface
- Communication system with secretary

---

### 6. SERVICE DES ÉTUDIANTS (Student Services)

**Dashboard Module:** `dashboard_student_services_app`

**Use Cases:**
- ✅ Enrollment Management - Register new students
- ✅ Re-enrollment Management - Annual re-registration
- ✅ Special Cases - Withdrawals, cancellations, exclusions
- ✅ Document Request Processing - Diplomas, certificates, transcripts
- ✅ Absence Justification Management
- ✅ Orientation & Counseling - Schedule sessions
- ✅ Scholarship Management - Update scholarship status
- ✅ Student Activities - Manage clubs, associations, events
- ✅ Student Record Updates - Maintain student information
- ✅ Decision Support - Generate reports and statistics

**Existing Models:**
- ✅ Student, Inscription (student_module)
- ✅ DocumentRequest, AbsenceJustification, StudentActivity, Scholarship, CounselingSession (dashboard_student_services_app)
- ⚠️ Request (document_module) - should be used instead of DocumentRequest

**Missing Features:**
- Special cases workflow (withdrawal, exclusion)
- Event management system
- Statistics generation interface

---

### 7. AGENT RECOUVREMENT DU MINERVAL (Collection Agent)

**Dashboard Module:** `dashboard_collection_agent_app`

**Use Cases:**
- ✅ Unpaid Data Extraction - Generate lists of students with unpaid fees
- ✅ Payment Recording - Record payments and issue receipts
- ✅ Notification Generation - Send automatic reminders
- ✅ Payment Installment Management - Manage payment plans
- ✅ Derogation Management - Handle payment exceptions
- ✅ Correspondence Management - Send official letters
- ✅ Targeted Communication - Message debtors
- ✅ Payment Schedule Proposals - Create payment plans
- ✅ Payment Promise Tracking - Monitor commitments
- ✅ Status Updates - Update payment status
- ✅ Administrative Alerts - Flag non-payment cases
- ✅ Litigation Preparation - Prepare legal case documents

**Existing Models:**
- ✅ Payment, FeesSheet (finance_module)
- ✅ PaymentInstallment, PaymentReminder, PaymentPlan, PaymentPromise, CollectionCorrespondence, LegalCase (dashboard_collection_agent_app)
- ✅ Notification, Message (dashboard_shared_app)

**Missing Features:**
- Automatic reminder system
- Payment plan calculator
- Report generation for unpaid fees

---

### 8. ÉTUDIANTS (Students)

**Dashboard Module:** `dashboard_student_app`

**Use Cases:**
- ✅ Enrollment/Re-enrollment - Complete forms, pay fees
- ✅ Profile Updates - Manage personal information
- ✅ Grade Consultation - View results (WITH PAYMENT CONDITION)
- ✅ Transcripts & Bulletins - Download (ONLY WHEN YEAR CLOSED)
- ✅ Progress Tracking - View credits and advancement
- ✅ Schedule - View timetable
- ✅ Academic Calendar - View important dates
- ✅ Absence Management - View attendance record
- ✅ Integrated Messaging - Communicate with professors/admin
- ⚠️ LMS Integration - Course platform (future)
- ✅ Notifications - Receive alerts
- ✅ Immediate Document Download - Certificates, transcripts
- ✅ Specific Document Requests - Submit requests for official documents

**Existing Models:**
- ✅ Student, Inscription (student_module)
- ✅ Result, CompiledResult (exam_module)
- ✅ Payment (finance_module)
- ✅ Timetable, Attendance (scheduling_module)
- ✅ Request (document_module)
- ✅ Notification, Message (dashboard_shared_app)
- ✅ StudentCard (student_module)

**Missing Features:**
- Payment condition check for grade access
- Year closure check for transcript access
- Automatic document generation (certificates)
- Document request status tracking

---

### 9. SECRÉTAIRES ACADÉMIQUES (Academic Secretaries)

**Dashboard Module:** `dashboard_academic_secretary_app`

**Use Cases:**
- ✅ Exam Organization - Plan calendar, assign supervisors, generate convocations
- ✅ Grade Coordination - Verify grade entry, calculate averages
- ✅ Jury Preparation - Generate deliberation documents
- ✅ Communication & Writing - Official notices, circulars
- ✅ Regulatory Compliance - Ensure conformity with regulations
- ⚠️ Exam & Logistics Management - Manage supervisors, attendance lists
- ✅ Copy Consultation & Complaints - Manage grade complaints
- ✅ Official Document Management - Circulation for signatures
- ✅ Teacher Payment Claim Entry - Validate and sign claims

**Existing Models:**
- ⚠️ ExamSession, ExamAttendance (dashboard_academic_secretary_app) - should use exam_module
- ✅ JurySession, JuryDecision (dashboard_academic_secretary_app)
- ✅ GradeComplaint (dashboard_academic_secretary_app)
- ✅ OfficialDocument (dashboard_academic_secretary_app)
- ✅ TeacherPaymentClaim (dashboard_academic_secretary_app)
- ✅ Exam, ExamRoom, ExamSupervisor (exam_module)
- ✅ Result (exam_module)

**Missing Features:**
- Exam convocation generation
- PV (procès-verbal) generation
- Electronic signature workflow
- Complaint resolution workflow

---

### 10. ALUMNI

**Dashboard Module:** `dashboard_alumni_app`

**Use Cases:**
- ✅ Professional Directory (CVthèque) - Update profile, search contacts
- ✅ Job & Internship Offers - Post opportunities
- ✅ Mentorship Programs - Register as mentor, guide students
- ✅ Testimonials & Content - Share experiences
- ✅ Event Participation - Register for events
- ✅ Donations & Fundraising - Make donations
- ✅ Ambassador Role - Represent the institution
- ✅ Academic Record Access - View diploma, transcripts
- ✅ Post-Graduation Resources - Access training, research
- ✅ Document Catalog - Request duplicates, certified transcripts

**Existing Models:**
- ✅ AlumniProfile, JobOffer, MentorshipProgram, AlumniTestimonial, AlumniEvent, AlumniEventRegistration, AlumniDonation (dashboard_alumni_app)
- ✅ Request (document_module) - for document requests

**Missing Features:**
- Alumni directory search
- Job board interface
- Mentor matching system
- Event ticketing integration
- Payment gateway for donations

---

## Mapping to Existing Models

### ✅ Fully Covered by Existing Models

| Use Case | Existing Model(s) | Location |
|----------|-------------------|----------|
| User Management | User, Role | foundational_service/auth_module |
| Student Profile | Student | student_module |
| Enrollment | Inscription | student_module |
| Payments | Payment, FeesSheet | finance_module |
| Grades/Results | Result, CompiledResult | exam_module |
| Schedule | Timetable, ScheduleSlot | scheduling_module |
| Attendance | Attendance | scheduling_module |
| Exams | Exam, ExamType, ExamRoom | exam_module |
| Documents | Document, Request | document_module |
| Rooms | Room, Building | infrastructure_module |
| Teachers | Teacher, Attribution | academic_module |
| Academic Structure | University, Faculty, Department, Class, Module, Course | academic_module |
| Notifications | Notification, Message | dashboard_shared_app |
| Audit | AuditLog | dashboard_shared_app |

### ⚠️ Partially Covered - Needs Extension

| Use Case | Existing Model | What's Missing |
|----------|----------------|----------------|
| Payment Installments | FeesSheet (has JSON field) | Dedicated installment tracking with due dates |
| Document Requests | Request (generic) | Status workflow, notification integration |
| Program Management | Class, Module, Course | Dean-specific management interface |
| Quality Assurance | StudentSurvey | Survey creation, response collection |

### ❌ Not Covered - Needs New Models/Features

| Use Case | What's Needed |
|----------|---------------|
| Payment Condition for Grade Access | Business logic + middleware |
| Year Closure Check | AcademicYear status field |
| Automatic Document Generation | PDF generation service |
| Electronic Signature Workflow | Signature tracking model + process |
| LMS Integration | External API integration |
| Alumni Directory Search | Search interface + privacy settings |
| Mentor Matching | Matching algorithm + communication |

---

## Missing Models/Features

### Critical Missing Features

#### 1. **Payment Condition Check (Priority: HIGH)**
**Requirement:** Students can only access grades if they've paid the required installment

**Implementation:**
```python
# Add to FeesSheet or create PaymentCondition model
class PaymentCondition(models.Model):
    inscription = models.ForeignKey(Inscription, ...)
    minimum_paid_percentage = models.IntegerField(default=50)
    grade_access_enabled = models.BooleanField(default=False)

    def check_payment_status(self):
        # Calculate if student has paid enough
        pass
```

**Location:** `finance_module` or `dashboard_student_app/services.py`

#### 2. **Academic Year Closure Status (Priority: HIGH)**
**Requirement:** Transcripts only available when year is closed

**Implementation:**
```python
# Add field to AcademicYear model
class AcademicYear(models.Model):
    # ... existing fields
    is_closed = models.BooleanField(default=False)
    closed_date = models.DateField(null=True, blank=True)
```

**Location:** `academic_module/university_app/models.py`

#### 3. **Exam Convocation Generation (Priority: MEDIUM)**
**Requirement:** Generate individual exam convocations for students

**Implementation:**
- PDF generation service
- Email sending integration
- Convocation template

**Location:** `dashboard_academic_secretary_app/services.py`

#### 4. **Electronic Signature Workflow (Priority: MEDIUM)**
**Requirement:** Documents circulate for signature

**Implementation:**
```python
class DocumentSignature(models.Model):
    document = models.ForeignKey(OfficialDocument, ...)
    signer = models.ForeignKey(User, ...)
    signature_order = models.IntegerField()
    signed_at = models.DateTimeField(null=True)
    status = models.CharField(...)  # pending, signed, rejected
```

**Location:** `dashboard_academic_secretary_app/models.py`

#### 5. **Installment Management (Priority: HIGH)**
**Requirement:** Track payment installments with due dates

**Current:** FeesSheet has JSON field `installements`
**Better:** Dedicated model for tracking

Already exists in `dashboard_collection_agent_app/models.py`:
```python
class PaymentInstallment(models.Model):
    # Existing model - needs to be linked to FeesSheet
```

#### 6. **Special Cases Workflow (Priority: MEDIUM)**
**Requirement:** Handle withdrawals, exclusions, cancellations

**Implementation:**
```python
class StudentStatus(models.Model):
    STATUSES = (
        ('active', 'Active'),
        ('withdrawn', 'Withdrawn'),
        ('excluded', 'Excluded'),
        ('suspended', 'Suspended'),
        ('graduated', 'Graduated'),
    )
    inscription = models.ForeignKey(Inscription, ...)
    status = models.CharField(max_length=20, choices=STATUSES)
    reason = models.TextField()
    effective_date = models.DateField()
    processed_by = models.ForeignKey(User, ...)
```

**Location:** `dashboard_student_services_app/models.py`

---

## Implementation Priority

### Phase 1: Core Functionality (CRITICAL)
**Duration:** 2-3 weeks

1. ✅ **Super Admin Dashboard** (Already mostly done)
   - User management CRUD
   - Role management
   - System configuration
   - Audit log viewing
   - Backup management

2. **Student Dashboard** (Needs work)
   - Payment condition check implementation
   - Grade access control
   - Transcript access control (year closure)
   - Document download (auto-generated)
   - Document request workflow

3. **Collection Agent Dashboard** (Needs work)
   - Unpaid fees report generation
   - Payment installment tracking
   - Reminder system
   - Payment status updates

### Phase 2: Academic Management (HIGH)
**Duration:** 3-4 weeks

4. **Academic Secretary Dashboard** (Needs refactoring)
   - Remove duplicate exam models
   - Use exam_module models
   - Implement convocation generation
   - Grade coordination dashboard
   - Jury preparation tools
   - Complaint management workflow

5. **Student Services Dashboard** (Needs completion)
   - Enrollment/re-enrollment interface
   - Special cases workflow
   - Document processing workflow
   - Activity management
   - Scholarship tracking

6. **Dean Dashboard** (Needs creation)
   - Schedule planning interface
   - Teacher attribution management
   - Room coordination
   - Program management
   - Group assignment

### Phase 3: Oversight & Quality (MEDIUM)
**Duration:** 2-3 weeks

7. **Recteur Dashboard** (Partially done)
   - Payment derogation workflow
   - Attribution validation
   - Payment monitoring dashboard
   - Performance supervision
   - Quality report consultation

8. **Quality Director Dashboard** (Needs surveys)
   - Survey creation & management
   - Performance analytics
   - Retention/enrollment statistics
   - Compliance audit tracking
   - Report generation

### Phase 4: Community & Extended Features (LOW)
**Duration:** 2-3 weeks

9. **Alumni Dashboard** (Mostly done, needs features)
   - Directory search interface
   - Job board
   - Mentor matching
   - Event management
   - Donation system

10. **Additional Features**
    - Electronic signature workflow
    - LMS integration (future)
    - Advanced analytics
    - Mobile app support

---

## Detailed Implementation by Role

### 1. SUPER ADMIN - Implementation Details

**Status:** ~80% complete

**Files to Work On:**
- ✅ `dashboard_super_admin_app/models.py` - Cleaned up
- ✅ `dashboard_super_admin_app/serializers.py` - Updated
- ✅ `dashboard_super_admin_app/services.py` - Updated
- ✅ `dashboard_super_admin_app/views.py` - Updated
- ⚠️ Need to add: Emergency password reset, MFA management

**New Endpoints Needed:**
```python
# Emergency password reset
POST /api/dashboard/super-admin/users/{id}/emergency-reset/

# MFA management
POST /api/dashboard/super-admin/users/{id}/enable-2fa/
POST /api/dashboard/super-admin/users/{id}/disable-2fa/
```

**Services to Add:**
```python
class SuperAdminDashboardService:
    @staticmethod
    def emergency_password_reset(user_id, new_password, admin_user):
        """Reset user password in emergency"""
        # Implementation

    @staticmethod
    def manage_2fa(user_id, action, admin_user):
        """Enable/disable 2FA for users"""
        # Implementation
```

---

### 2. STUDENT - Implementation Details

**Status:** ~40% complete

**Critical Implementation: Payment Condition Check**

```python
# File: dashboard_student_app/services.py

class StudentDashboardService:
    @staticmethod
    def check_grade_access(student):
        """Check if student can access grades based on payment"""
        active_inscription = student.inscriptions.filter(
            is_year_close=False
        ).first()

        if not active_inscription:
            return False

        # Get fees for this inscription
        fees_sheet = FeesSheet.objects.filter(
            class_fk=active_inscription.class_fk,
            academic_year=active_inscription.academic_year
        ).first()

        if not fees_sheet:
            return True  # No fees = open access

        # Calculate total paid
        total_paid = Payment.objects.filter(
            inscription=active_inscription,
            payment_status='verified'
        ).aggregate(total=Sum('amount_paid'))['total'] or 0

        # Calculate required installment
        installments = fees_sheet.installements or []
        if not installments:
            return True

        # Check if current installment is paid
        current_date = timezone.now().date()
        required_amount = 0

        for installment in installments:
            if current_date >= installment.get('due_date'):
                required_amount += installment.get('amount', 0)

        return total_paid >= required_amount

    @staticmethod
    def get_student_grades_conditional(student):
        """Get grades only if payment conditions are met"""
        if not StudentDashboardService.check_grade_access(student):
            return {
                'error': 'PAYMENT_REQUIRED',
                'message': 'Vous devez payer la tranche exigée pour accéder à vos notes.'
            }

        return Result.objects.filter(
            inscription__student=student
        ).select_related('course', 'session')
```

**New View:**
```python
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def student_grades_view(request):
    """Get student grades with payment condition"""
    try:
        student = request.user.students_users
        grades_data = StudentDashboardService.get_student_grades_conditional(student)

        if 'error' in grades_data:
            return error_response(
                message=grades_data['message'],
                status_code=status.HTTP_402_PAYMENT_REQUIRED
            )

        serializer = StudentGradesSerializer(grades_data, many=True)
        return success_response(data=serializer.data)

    except Exception as e:
        return error_response(str(e))
```

---

### 3. COLLECTION AGENT - Implementation Details

**Status:** ~60% complete (models exist, need services)

**Critical Services Needed:**

```python
# File: dashboard_collection_agent_app/services.py

class CollectionAgentService:
    @staticmethod
    def generate_unpaid_report(filters=None):
        """Generate report of students with unpaid fees"""
        # Get all active inscriptions
        inscriptions = Inscription.objects.filter(
            regist_status='ACT',
            is_year_close=False
        )

        unpaid_students = []

        for inscription in inscriptions:
            # Calculate total fees
            fees = FeesSheet.objects.filter(
                class_fk=inscription.class_fk,
                academic_year=inscription.academic_year
            ).first()

            if not fees:
                continue

            total_fees = fees.base_amount

            # Calculate total paid
            total_paid = Payment.objects.filter(
                inscription=inscription,
                payment_status='verified'
            ).aggregate(total=Sum('amount_paid'))['total'] or 0

            balance = total_fees - total_paid

            if balance > 0:
                unpaid_students.append({
                    'student': inscription.student,
                    'inscription': inscription,
                    'total_fees': total_fees,
                    'total_paid': total_paid,
                    'balance': balance,
                    'days_overdue': calculate_days_overdue(inscription)
                })

        return unpaid_students

    @staticmethod
    def create_payment_plan(student_id, plan_data, agent_user):
        """Create a payment plan for a student"""
        student = Student.objects.get(id=student_id)
        inscription = student.inscriptions.filter(is_year_close=False).first()

        payment_plan = PaymentPlan.objects.create(
            student=student,
            inscription=inscription,
            total_amount=plan_data['total_amount'],
            created_by=agent_user
        )

        # Create installments
        for installment_data in plan_data['installments']:
            PaymentInstallment.objects.create(
                payment_plan=payment_plan,
                amount=installment_data['amount'],
                due_date=installment_data['due_date']
            )

        return payment_plan

    @staticmethod
    def send_payment_reminder(student_id, reminder_type):
        """Send payment reminder to student"""
        student = Student.objects.get(id=student_id)

        # Create reminder record
        reminder = PaymentReminder.objects.create(
            student=student,
            reminder_type=reminder_type,
            sent_date=timezone.now()
        )

        # Create notification
        Notification.objects.create(
            recipient=student.user,
            recipient_type='student',
            notification_type='payment',
            title='Rappel de Paiement',
            message=get_reminder_message(reminder_type)
        )

        # TODO: Send email/SMS

        return reminder
```

---

## Next Steps

1. **Review and Approve Plan** - Get stakeholder approval
2. **Set Up Project Board** - Track implementation progress
3. **Start Phase 1** - Implement critical features first
4. **Iterative Development** - Build, test, deploy in sprints
5. **User Testing** - Get feedback from each role
6. **Documentation** - API docs, user manuals

---

**Generated by:** Claude Code AI Assistant
**Date:** 2025-11-17
**Purpose:** Complete implementation roadmap for UMS dashboards
