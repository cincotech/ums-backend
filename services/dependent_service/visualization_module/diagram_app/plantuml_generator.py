import csv
from pathlib import Path

from django.apps import apps


class PlantUMLGenerator:
    """Generate PlantUML diagrams for Django models"""

    def __init__(self, output_dir="docs/diagrams/plantuml"):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)

    def _load_roles(self):
        roles_path = Path("roles.csv")
        if not roles_path.exists():
            return []

        roles = []
        with roles_path.open(newline="", encoding="utf-8") as handle:
            reader = csv.DictReader(handle)
            for row in reader:
                name = (row.get("name") or "").strip()
                description = (row.get("description") or "").strip()
                if name:
                    roles.append({"name": name, "description": description})
        return roles

    def _role_label(self, role_name):
        return role_name.replace("_", " ").title()

    def generate_class_diagram(self, module_filter=None):
        """Generate UML Class Diagram"""
        content = ["@startuml", "skinparam linetype ortho", ""]

        for model in apps.get_models():
            if module_filter and module_filter not in model._meta.app_label:
                continue

            content.append(f"class {model.__name__} {{")

            for field in model._meta.get_fields():
                if hasattr(field, "get_internal_type"):
                    field_type = field.get_internal_type()
                    content.append(f"  +{field.name}: {field_type}")

            content.append("}")
            content.append("")

        # Relationships
        for model in apps.get_models():
            if module_filter and module_filter not in model._meta.app_label:
                continue

            for field in model._meta.get_fields():
                if field.many_to_one:
                    content.append(
                        f"{model.__name__} --> {field.related_model.__name__}"
                    )
                elif field.many_to_many:
                    content.append(
                        f"{model.__name__} --* {field.related_model.__name__}"
                    )
                elif field.one_to_one:
                    content.append(
                        f"{model.__name__} -- {field.related_model.__name__}"
                    )

        content.append("@enduml")

        filename = f"class_diagram_{module_filter or 'all'}.puml"
        (self.output_dir / filename).write_text("\n".join(content))
        return filename

    def generate_object_diagram(self, module_filter=None):
        """Generate UML Object Diagram"""
        content = ["@startuml", ""]

        for model in apps.get_models():
            if module_filter and module_filter not in model._meta.app_label:
                continue

            content.append(f'object "{model.__name__}" as {model.__name__} {{')
            for field in model._meta.get_fields():
                if hasattr(field, "get_internal_type"):
                    content.append(f"  {field.name}")
            content.append("}")
            content.append("")

        content.append("@enduml")

        filename = f"object_diagram_{module_filter or 'all'}.puml"
        (self.output_dir / filename).write_text("\n".join(content))
        return filename

    def generate_component_diagram(self):
        """Generate UML Component Diagram"""
        content = ["@startuml", ""]

        services = {
            "foundational_service": ["geo_module", "auth_module"],
            "core_service": ["academic_module", "student_module"],
            "dependent_service": [
                "document_module",
                "exam_module",
                "infrastructure_module",
                "notification_module",
                "scheduling_module",
                "dashboard_module",
            ],
        }

        for service, modules in services.items():
            content.append(f"package {service} {{")
            for module in modules:
                content.append(f"  component {module}")
            content.append("}")
            content.append("")

        content.append("foundational_service --> core_service")
        content.append("core_service --> dependent_service")
        content.append("@enduml")

        filename = "component_diagram.puml"
        (self.output_dir / filename).write_text("\n".join(content))
        return filename

    def generate_deployment_diagram(self):
        """Generate UML Deployment Diagram"""
        content = [
            "@startuml",
            "",
            'node "Web Server" {',
            "  [Django Application]",
            "  [Static Files]",
            "}",
            "",
            'node "Database Server" {',
            '  database "PostgreSQL/MySQL" {',
            "    [UMS Database]",
            "  }",
            "}",
            "",
            'node "Cache Server" {',
            "  [Redis]",
            "}",
            "",
            "[Django Application] --> [UMS Database]",
            "[Django Application] --> [Redis]",
            "",
            "@enduml",
        ]

        filename = "deployment_diagram.puml"
        (self.output_dir / filename).write_text("\n".join(content))
        return filename

    def generate_use_case_diagram(self):
        """Generate UML Use Case Diagram with role-based actors from roles.csv"""
        use_cases = [
            ("UC1", "Manage System Configuration"),
            ("UC2", "Backup & Restore System"),
            ("UC3", "Manage Users & Roles"),
            ("UC4", "Approve Programs"),
            ("UC5", "Review Academic Programs"),
            ("UC6", "Quality Audit & Compliance"),
            ("UC7", "Manage Faculty & Teaching Loads"),
            ("UC8", "Manage Courses & Schedules"),
            ("UC9", "Manage Registrations"),
            ("UC10", "Manage Documents"),
            ("UC11", "Manage Payments & Fees"),
            ("UC12", "Oversee Academic Affairs"),
            ("UC13", "Submit Grades"),
            ("UC14", "Record Attendance"),
            ("UC15", "Mentor Students"),
            ("UC16", "Register Courses"),
            ("UC17", "View Grades"),
            ("UC18", "Request Documents"),
            ("UC19", "Access Alumni Portal"),
            ("UC20", "Post Alumni Events/Jobs"),
            ("UC21", "Represent Class & Communicate"),
            ("UC22", "Administrative Support"),
        ]

        role_to_usecases = {
            "super_admin": ["UC1", "UC2", "UC3"],
            "rector": ["UC4"],
            "director_academic": ["UC5"],
            "director_quality_assurance": ["UC6"],
            "dean": ["UC7", "UC8"],
            "student_service": ["UC9", "UC10"],
            "finance_service": ["UC11"],
            "general_service": ["UC22"],
            "rector_office": ["UC4", "UC22"],
            "academic_affairs": ["UC12"],
            "teacher": ["UC13", "UC14"],
            "supervisor": ["UC15"],
            "student": ["UC16", "UC17", "UC18", "UC11"],
            "alumni": ["UC19", "UC20", "UC18"],
            "delegate": ["UC21"],
        }

        roles = self._load_roles()
        if not roles:
            roles = [
                {"name": name, "description": ""} for name in role_to_usecases.keys()
            ]

        content = ["@startuml", "left to right direction", ""]

        for role in roles:
            role_name = role["name"]
            label = self._role_label(role_name)
            content.append(f'actor "{label}" as {role_name}')

        content.append("")
        content.append("rectangle UMS {")
        for usecase_id, usecase_label in use_cases:
            content.append(f'  usecase "{usecase_label}" as {usecase_id}')
        content.append("}")
        content.append("")

        for role in roles:
            role_name = role["name"]
            for usecase_id in role_to_usecases.get(role_name, []):
                content.append(f"{role_name} --> {usecase_id}")

        content.append("")
        content.append("@enduml")

        filename = "use_case_diagram.puml"
        (self.output_dir / filename).write_text("\n".join(content))
        return filename

    def generate_role_hierarchy_diagram(self):
        """Generate role hierarchy diagram"""
        content = [
            "@startuml",
            "",
            "class Role {",
            "  +id: UUID",
            "  +name: String",
            "  +description: String",
            "}",
            "",
            "class User {",
            "  +id: UUID",
            "  +email: String",
            "  +role: ForeignKey",
            "}",
            "",
            "class Profile {",
            "  +user: OneToOne",
            "  +dean_fields",
            "  +rector_fields",
            "  +service_fields",
            "}",
            "",
            "User --> Role",
            "Profile --> User",
            "",
            "note right of Role",
            "  Roles:",
            "  - super_admin",
            "  - rector",
            "  - director_academic",
            "  - director_quality_assurance",
            "  - dean",
            "  - student_service",
            "  - finance_service",
            "  - general_service",
            "  - rector_office",
            "  - academic_affairs",
            "  - teacher",
            "  - supervisor",
            "  - student",
            "  - alumni",
            "  - delegate",
            "end note",
            "",
            "@enduml",
        ]

        filename = "role_hierarchy_diagram.puml"
        (self.output_dir / filename).write_text("\n".join(content))
        return filename

    def generate_sequence_diagram(self, scenario="student_registration"):
        """Generate UML Sequence Diagram"""
        scenarios = {
            "student_registration": [
                "@startuml",
                "skinparam responseMessageBelowArrow true",
                "skinparam sequenceMessageAlign center",
                "autonumber",
                "actor Student",
                'participant "Registration API" as API',
                'participant "Student Service" as Service',
                'database "Database" as DB',
                "",
                "Student -> API: POST /api/register",
                "API -> Service: create_student(data)",
                "Service -> DB: save(student)",
                "DB --> Service: student_id",
                "Service --> API: success",
                "API --> Student: 201 Created",
                "@enduml",
            ],
            "grade_submission": [
                "@startuml",
                "skinparam responseMessageBelowArrow true",
                "skinparam sequenceMessageAlign center",
                "autonumber",
                "actor Teacher",
                'participant "Grade API" as API',
                'participant "Result Service" as Service',
                'database "Database" as DB',
                "",
                "Teacher -> API: POST /api/grades",
                "API -> Service: submit_grade(data)",
                "Service -> DB: save(grade)",
                "DB --> Service: grade_id",
                "Service --> API: success",
                "API --> Teacher: 200 OK",
                "@enduml",
            ],
            "auth_login_flow": [
                "@startuml",
                "skinparam responseMessageBelowArrow true",
                "skinparam sequenceMessageAlign center",
                "autonumber",
                "actor User",
                'participant "Auth API" as API',
                'participant "Auth Service" as Service',
                'database "User Store" as DB',
                'participant "Token Service" as Token',
                'participant "Notification Service" as Notify',
                "",
                "User -> API: POST /auth/login",
                "API -> Service: validate_credentials(email, password)",
                "Service -> DB: get_user(email)",
                "DB --> Service: user",
                "alt Invalid credentials",
                "  Service --> API: auth_failed",
                "  API --> User: 401 Unauthorized",
                "else Valid credentials",
                "  Service -> Token: generate_tokens(user)",
                "  Token --> Service: access + refresh",
                "  Service -> Notify: create_login_notice(user)",
                "  Notify --> Service: created",
                "  Service --> API: tokens + profile",
                "  API --> User: 200 OK",
                "end",
                "@enduml",
            ],
            "student_inscription_flow": [
                "@startuml",
                "skinparam responseMessageBelowArrow true",
                "skinparam sequenceMessageAlign center",
                "autonumber",
                "actor Student",
                'participant "Inscription API" as API',
                'participant "Inscription Service" as Service',
                'database "Student" as StudentDB',
                'database "Class" as ClassDB',
                'database "AcademicYear" as YearDB',
                'database "Inscription" as InscriptionDB',
                'participant "Payment Service" as Payment',
                'participant "Notification Service" as Notify',
                "",
                "Student -> API: POST /inscriptions",
                "API -> Service: validate_request(payload)",
                "Service -> StudentDB: get_student(student_id)",
                "StudentDB --> Service: student",
                "Service -> ClassDB: get_class(class_id)",
                "ClassDB --> Service: class",
                "Service -> YearDB: get_academic_year(year_id)",
                "YearDB --> Service: academic_year",
                "Service -> InscriptionDB: create_inscription(student, class, year)",
                "InscriptionDB --> Service: inscription",
                "Service -> Payment: create_payment_plan(inscription)",
                "Payment --> Service: payment_plan",
                "Service -> Notify: send_inscription_confirmation(student)",
                "Notify --> Service: sent",
                "Service --> API: success",
                "API --> Student: 201 Created",
                "@enduml",
            ],
            "dashboard_notifications_flow": [
                "@startuml",
                "skinparam responseMessageBelowArrow true",
                "skinparam sequenceMessageAlign center",
                "autonumber",
                'actor "Dashboard User" as User',
                'participant "Dashboard API" as API',
                'participant "Notification Service" as Service',
                'database "Notification" as DB',
                "",
                "User -> API: GET /dashboard/notifications",
                "API -> Service: list_notifications(user)",
                "Service -> DB: fetch_by_user(user)",
                "DB --> Service: notifications",
                "Service --> API: notifications",
                "API --> User: 200 OK",
                "",
                "User -> API: PATCH /dashboard/notifications/{id}",
                "API -> Service: mark_read(notification_id)",
                "Service -> DB: update_is_read(true)",
                "DB --> Service: updated",
                "Service --> API: ok",
                "API --> User: 200 OK",
                "@enduml",
            ],
            "dashboard_payment_collection_flow": [
                "@startuml",
                "skinparam responseMessageBelowArrow true",
                "skinparam sequenceMessageAlign center",
                "autonumber",
                'actor "Collection Agent" as Agent',
                'participant "Dashboard Collection API" as API',
                'participant "Payment Service" as Service',
                'database "PaymentPlan" as PlanDB',
                'database "PaymentInstallement" as InstallmentDB',
                'database "Student" as StudentDB',
                'participant "Notification Service" as Notify',
                "",
                "Agent -> API: POST /dashboard/collection/payments",
                "API -> Service: record_payment(student_id, amount)",
                "Service -> StudentDB: get_student(student_id)",
                "StudentDB --> Service: student",
                "Service -> PlanDB: get_active_plan(student)",
                "PlanDB --> Service: plan",
                "Service -> InstallmentDB: apply_payment(plan, amount)",
                "InstallmentDB --> Service: installment_updated",
                "Service -> Notify: send_payment_receipt(student)",
                "Notify --> Service: sent",
                "Service --> API: success",
                "API --> Agent: 200 OK",
                "@enduml",
            ],
        }

        content = scenarios.get(scenario, scenarios["student_registration"])
        filename = f"sequence_diagram_{scenario}.puml"
        (self.output_dir / filename).write_text("\n".join(content))
        return filename

    def generate_activity_diagram(self, process="student_enrollment"):
        """Generate UML Activity Diagram"""
        processes = {
            # Auth workflows
            "auth_login": [
                "@startuml",
                "start",
                ":User enters credentials;",
                "if (Valid credentials?) then (yes)",
                "  if (2FA enabled?) then (yes)",
                "    :Send OTP;",
                "    :Verify OTP;",
                "    if (OTP valid?) then (yes)",
                "      :Generate JWT tokens;",
                "      :Return tokens;",
                "    else (no)",
                "      :Return 401;",
                "    endif",
                "  else (no)",
                "    :Generate JWT tokens;",
                "    :Return tokens;",
                "  endif",
                "else (no)",
                "  :Return 401;",
                "endif",
                "stop",
                "@enduml",
            ],
            "auth_register": [
                "@startuml",
                "start",
                ":User submits registration;",
                ":Validate data;",
                "if (Valid?) then (yes)",
                "  :Create user account;",
                "  :Assign role;",
                "  :Send verification email;",
                "  :Return success;",
                "else (no)",
                "  :Return validation errors;",
                "endif",
                "stop",
                "@enduml",
            ],
            "auth_password_reset": [
                "@startuml",
                "start",
                ":User requests password reset;",
                ":Validate email;",
                "if (Email exists?) then (yes)",
                "  :Generate reset token;",
                "  :Send reset email;",
                "  :User clicks link;",
                "  :Enter new password;",
                "  :Update password;",
                "  :Return success;",
                "else (no)",
                "  :Return error;",
                "endif",
                "stop",
                "@enduml",
            ],
            # Student workflows
            "student_enrollment": [
                "@startuml",
                "start",
                ":Student submits application;",
                "if (Documents complete?) then (yes)",
                "  :Verify documents;",
                "  if (Valid?) then (yes)",
                "    :Create student profile;",
                "    :Generate student ID;",
                "    :Send confirmation;",
                "  else (no)",
                "    :Reject application;",
                "  endif",
                "else (no)",
                "  :Request missing documents;",
                "endif",
                "stop",
                "@enduml",
            ],
            "student_course_registration": [
                "@startuml",
                "start",
                ":Student selects courses;",
                ":Check prerequisites;",
                "if (Prerequisites met?) then (yes)",
                "  :Check course capacity;",
                "  if (Space available?) then (yes)",
                "    :Register student;",
                "    :Update enrollment;",
                "    :Send confirmation;",
                "  else (no)",
                "    :Add to waitlist;",
                "  endif",
                "else (no)",
                "  :Show prerequisite error;",
                "endif",
                "stop",
                "@enduml",
            ],
            "student_document_request": [
                "@startuml",
                "start",
                ":Student requests document;",
                ":Student service validates;",
                "if (Valid request?) then (yes)",
                "  :Process request;",
                "  :Generate document;",
                "  :Notify student;",
                "else (no)",
                "  :Reject with reason;",
                "endif",
                "stop",
                "@enduml",
            ],
            # Teacher workflows
            "teacher_grade_submission": [
                "@startuml",
                "start",
                ":Teacher enters grades;",
                ":Validate grade data;",
                "if (Valid?) then (yes)",
                "  :Save grades;",
                "  :Calculate statistics;",
                "  :Notify students;",
                "else (no)",
                "  :Show validation errors;",
                "endif",
                "stop",
                "@enduml",
            ],
            "teacher_attendance": [
                "@startuml",
                "start",
                ":Teacher marks attendance;",
                ":Select class session;",
                ":Mark present/absent;",
                ":Submit attendance;",
                ":Update records;",
                ":Notify absent students;",
                "stop",
                "@enduml",
            ],
            # Dean workflows
            "dean_course_management": [
                "@startuml",
                "start",
                ":Dean reviews courses;",
                ":Check teaching progress;",
                "if (Teacher available?) then (yes)",
                "  :Assign teacher;",
                "  :Update workload;",
                "  :Notify teacher;",
                "else (no)",
                "  :Request visitor teacher;",
                "  :Rector approves;",
                "  :Assign visitor;",
                "endif",
                "stop",
                "@enduml",
            ],
            "dean_faculty_management": [
                "@startuml",
                "start",
                ":Dean manages faculty;",
                ":Review departments;",
                ":Monitor programs;",
                ":Check teacher workload;",
                ":Generate reports;",
                "stop",
                "@enduml",
            ],
            # Rector workflows
            "rector_payment_derogation": [
                "@startuml",
                "start",
                ":Student requests derogation;",
                ":Finance reviews;",
                ":Forward to rector;",
                "if (Rector approves?) then (yes)",
                "  :Create derogation;",
                "  :Update payment plan;",
                "  :Notify student;",
                "else (no)",
                "  :Reject request;",
                "endif",
                "stop",
                "@enduml",
            ],
            "rector_program_approval": [
                "@startuml",
                "start",
                ":Dean submits program;",
                ":Rector reviews;",
                "if (Meets standards?) then (yes)",
                "  :Approve program;",
                "  :Publish program;",
                "  :Notify stakeholders;",
                "else (no)",
                "  :Request revisions;",
                "endif",
                "stop",
                "@enduml",
            ],
            # Quality Director workflows
            "quality_audit": [
                "@startuml",
                "start",
                ":Quality director initiates audit;",
                ":Define standards;",
                ":Conduct compliance audit;",
                ":Generate report;",
                "if (Standards met?) then (yes)",
                "  :Approve program;",
                "  :Track execution;",
                "else (no)",
                "  :Create improvement plan;",
                "  :Schedule re-audit;",
                "endif",
                "stop",
                "@enduml",
            ],
            "quality_satisfaction_survey": [
                "@startuml",
                "start",
                ":Create survey;",
                ":Distribute to students;",
                ":Collect responses;",
                ":Analyze results;",
                ":Generate report;",
                ":Share with stakeholders;",
                "stop",
                "@enduml",
            ],
            # Collection Agent workflows
            "payment_collection": [
                "@startuml",
                "start",
                ":Agent reviews fees;",
                "if (Payment overdue?) then (yes)",
                "  :Send reminder;",
                "  if (Payment received?) then (yes)",
                "    :Record payment;",
                "    :Update fees sheet;",
                "    :Send receipt;",
                "  else (no)",
                "    :Create payment promise;",
                "    :Schedule follow-up;",
                "  endif",
                "else (no)",
                "  :Mark as current;",
                "endif",
                "stop",
                "@enduml",
            ],
            "payment_plan_creation": [
                "@startuml",
                "start",
                ":Agent creates payment plan;",
                ":Define installments;",
                ":Set due dates;",
                ":Assign to student;",
                ":Send notification;",
                ":Schedule reminders;",
                "stop",
                "@enduml",
            ],
            # Student Services workflows
            "student_service_scholarship": [
                "@startuml",
                "start",
                ":Student applies for scholarship;",
                ":Service validates eligibility;",
                "if (Eligible?) then (yes)",
                "  :Review application;",
                "  if (Approved?) then (yes)",
                "    :Award scholarship;",
                "    :Update student record;",
                "    :Notify student;",
                "  else (no)",
                "    :Reject application;",
                "  endif",
                "else (no)",
                "  :Return ineligible;",
                "endif",
                "stop",
                "@enduml",
            ],
            "student_service_counseling": [
                "@startuml",
                "start",
                ":Student requests counseling;",
                ":Schedule session;",
                ":Conduct session;",
                ":Record notes;",
                ":Follow-up if needed;",
                "stop",
                "@enduml",
            ],
            # Alumni workflows
            "alumni_event": [
                "@startuml",
                "start",
                ":Alumni creates event;",
                ":Set event details;",
                ":Publish event;",
                ":Alumni register;",
                ":Send reminders;",
                ":Event occurs;",
                ":Collect testimonials;",
                "stop",
                "@enduml",
            ],
            "alumni_job_posting": [
                "@startuml",
                "start",
                ":Alumni posts job offer;",
                ":Validate job details;",
                ":Publish job;",
                ":Notify alumni network;",
                ":Track applications;",
                "stop",
                "@enduml",
            ],
            # Academic Secretary workflows
            "secretary_schedule_management": [
                "@startuml",
                "start",
                ":Secretary creates schedule;",
                ":Assign rooms;",
                ":Assign time slots;",
                ":Check conflicts;",
                "if (Conflicts?) then (yes)",
                "  :Resolve conflicts;",
                "else (no)",
                "  :Publish schedule;",
                "  :Notify teachers/students;",
                "endif",
                "stop",
                "@enduml",
            ],
            # Super Admin workflows
            "super_admin_config": [
                "@startuml",
                "start",
                ":Super admin accesses system;",
                "if (Action?) then (config)",
                "  :Update configuration;",
                "  :Log audit trail;",
                "elseif (backup)",
                "  :Create backup;",
                "  :Store backup record;",
                "elseif (emergency)",
                "  :Activate recovery;",
                "  :Execute recovery;",
                "endif",
                ":Notify admins;",
                "stop",
                "@enduml",
            ],
            "super_admin_university_setup": [
                "@startuml",
                "start",
                ":Create university profile;",
                ":Configure modules;",
                ":Set subscription;",
                ":Create admin accounts;",
                ":Initialize system;",
                ":Activate university;",
                "stop",
                "@enduml",
            ],
            # Academic Director workflows
            "academic_director_program_review": [
                "@startuml",
                "start",
                ":Director reviews programs;",
                ":Check curriculum;",
                ":Validate courses;",
                "if (Approved?) then (yes)",
                "  :Forward to rector;",
                "else (no)",
                "  :Request revisions;",
                "endif",
                "stop",
                "@enduml",
            ],
            # Exam workflows
            "exam_session_creation": [
                "@startuml",
                "start",
                ":Create exam session;",
                ":Define exam dates;",
                ":Assign courses;",
                ":Notify teachers;",
                ":Teachers submit grades;",
                ":Compile results;",
                ":Publish results;",
                "stop",
                "@enduml",
            ],
            # Document workflows
            "document_generation": [
                "@startuml",
                "start",
                ":Request document;",
                ":Validate request;",
                "if (Valid?) then (yes)",
                "  :Generate document;",
                "  :Sign document;",
                "  :Store document;",
                "  :Notify requester;",
                "else (no)",
                "  :Reject request;",
                "endif",
                "stop",
                "@enduml",
            ],
        }

        content = processes.get(process, processes["student_enrollment"])
        filename = f"activity_diagram_{process}.puml"
        (self.output_dir / filename).write_text("\n".join(content))
        return filename

    def generate_all(self, module_filter=None):
        """Generate all UML diagrams"""
        generated = []

        # Structure diagrams
        generated.append(self.generate_class_diagram(module_filter))
        generated.append(self.generate_object_diagram(module_filter))
        generated.append(self.generate_component_diagram())
        generated.append(self.generate_deployment_diagram())
        generated.append(self.generate_use_case_diagram())
        generated.append(self.generate_role_hierarchy_diagram())

        # Sequence diagrams
        generated.append(self.generate_sequence_diagram("student_registration"))
        generated.append(self.generate_sequence_diagram("grade_submission"))
        generated.append(self.generate_sequence_diagram("auth_login_flow"))
        generated.append(self.generate_sequence_diagram("student_inscription_flow"))
        generated.append(self.generate_sequence_diagram("dashboard_notifications_flow"))
        generated.append(
            self.generate_sequence_diagram("dashboard_payment_collection_flow")
        )

        # Activity diagrams - Auth
        generated.append(self.generate_activity_diagram("auth_login"))
        generated.append(self.generate_activity_diagram("auth_register"))
        generated.append(self.generate_activity_diagram("auth_password_reset"))

        # Activity diagrams - Student
        generated.append(self.generate_activity_diagram("student_enrollment"))
        generated.append(self.generate_activity_diagram("student_course_registration"))
        generated.append(self.generate_activity_diagram("student_document_request"))

        # Activity diagrams - Teacher
        generated.append(self.generate_activity_diagram("teacher_grade_submission"))
        generated.append(self.generate_activity_diagram("teacher_attendance"))

        # Activity diagrams - Dean
        generated.append(self.generate_activity_diagram("dean_course_management"))
        generated.append(self.generate_activity_diagram("dean_faculty_management"))

        # Activity diagrams - Rector
        generated.append(self.generate_activity_diagram("rector_payment_derogation"))
        generated.append(self.generate_activity_diagram("rector_program_approval"))

        # Activity diagrams - Quality Director
        generated.append(self.generate_activity_diagram("quality_audit"))
        generated.append(self.generate_activity_diagram("quality_satisfaction_survey"))

        # Activity diagrams - Collection Agent
        generated.append(self.generate_activity_diagram("payment_collection"))
        generated.append(self.generate_activity_diagram("payment_plan_creation"))

        # Activity diagrams - Student Services
        generated.append(self.generate_activity_diagram("student_service_scholarship"))
        generated.append(self.generate_activity_diagram("student_service_counseling"))

        # Activity diagrams - Alumni
        generated.append(self.generate_activity_diagram("alumni_event"))
        generated.append(self.generate_activity_diagram("alumni_job_posting"))

        # Activity diagrams - Academic Secretary
        generated.append(
            self.generate_activity_diagram("secretary_schedule_management")
        )

        # Activity diagrams - Super Admin
        generated.append(self.generate_activity_diagram("super_admin_config"))
        generated.append(self.generate_activity_diagram("super_admin_university_setup"))

        # Activity diagrams - Academic Director
        generated.append(
            self.generate_activity_diagram("academic_director_program_review")
        )

        # Activity diagrams - Exam & Document
        generated.append(self.generate_activity_diagram("exam_session_creation"))
        generated.append(self.generate_activity_diagram("document_generation"))

        return generated
