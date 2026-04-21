from pathlib import Path


class ComponentDetailGenerator:
    """Generate Detailed Component Diagrams for Each Module"""

    def __init__(self, output_dir="docs/diagrams/plantuml/components"):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)

    def generate_academic_module_component(self):
        content = [
            "@startuml",
            "package academic_module {",
            "  component university_app {",
            "    [University Management]",
            "    [Faculty Management]",
            "    [Department Management]",
            "  }",
            "  ",
            "  component program_app {",
            "    [Program Management]",
            "    [Course Management]",
            "    [Curriculum Management]",
            "  }",
            "  ",
            "  component class_app {",
            "    [Class Management]",
            "    [Academic Year Management]",
            "    [Classroom Management]",
            "  }",
            "  ",
            "  component result_app {",
            "    [Grade Management]",
            "    [Transcript Generation]",
            "    [Result Publishing]",
            "  }",
            "  ",
            "  database academic_db",
            "  ",
            "  university_app --> academic_db",
            "  program_app --> academic_db",
            "  class_app --> academic_db",
            "  result_app --> academic_db",
            "  ",
            "  university_app --> program_app",
            "  program_app --> class_app",
            "  class_app --> result_app",
            "}",
            "@enduml",
        ]
        filename = "academic_module_component_detail.puml"
        (self.output_dir / filename).write_text("\n".join(content))
        return filename

    def generate_financial_module_component(self):
        content = [
            "@startuml",
            "package financial_module {",
            "  component payment_app {",
            "    [Payment Processing]",
            "    [Payment Plan Management]",
            "    [Installment Tracking]",
            "    [Receipt Generation]",
            "  }",
            "  ",
            "  component fee_app {",
            "    [Fee Structure Management]",
            "    [Fee Category Management]",
            "    [Fee Calculation]",
            "  }",
            "  ",
            "  component derogation_app {",
            "    [Derogation Request]",
            "    [Derogation Approval]",
            "    [Derogation Tracking]",
            "  }",
            "  ",
            "  component scholarship_app {",
            "    [Scholarship Management]",
            "    [Application Processing]",
            "    [Award Management]",
            "  }",
            "  ",
            "  database financial_db",
            "  ",
            "  payment_app --> financial_db",
            "  fee_app --> financial_db",
            "  derogation_app --> financial_db",
            "  scholarship_app --> financial_db",
            "  ",
            "  fee_app --> payment_app",
            "  payment_app --> derogation_app",
            "  scholarship_app --> payment_app",
            "}",
            "@enduml",
        ]
        filename = "financial_module_component_detail.puml"
        (self.output_dir / filename).write_text("\n".join(content))
        return filename

    def generate_scheduling_module_component(self):
        content = [
            "@startuml",
            "package scheduling_module {",
            "  component schedule_app {",
            "    [Schedule Creation]",
            "    [Time Slot Management]",
            "    [Conflict Detection]",
            "    [Schedule Publishing]",
            "  }",
            "  ",
            "  component timetable_app {",
            "    [Timetable Generation]",
            "    [Teacher Assignment]",
            "    [Room Allocation]",
            "  }",
            "  ",
            "  component attendance_app {",
            "    [Attendance Recording]",
            "    [Attendance Tracking]",
            "    [Attendance Reports]",
            "  }",
            "  ",
            "  database scheduling_db",
            "  ",
            "  schedule_app --> scheduling_db",
            "  timetable_app --> scheduling_db",
            "  attendance_app --> scheduling_db",
            "  ",
            "  schedule_app --> timetable_app",
            "  timetable_app --> attendance_app",
            "}",
            "@enduml",
        ]
        filename = "scheduling_module_component_detail.puml"
        (self.output_dir / filename).write_text("\n".join(content))
        return filename

    def generate_notification_module_component(self):
        content = [
            "@startuml",
            "package notification_module {",
            "  component notification_app {",
            "    [Notification Creation]",
            "    [Notification Queue]",
            "    [Notification Delivery]",
            "    [Notification Tracking]",
            "  }",
            "  ",
            "  component email_app {",
            "    [Email Service]",
            "    [Email Templates]",
            "    [Email Queue]",
            "  }",
            "  ",
            "  component sms_app {",
            "    [SMS Service]",
            "    [SMS Templates]",
            "    [SMS Queue]",
            "  }",
            "  ",
            "  component push_app {",
            "    [Push Notification Service]",
            "    [Device Management]",
            "  }",
            "  ",
            "  database notification_db",
            "  queue message_queue",
            "  ",
            "  notification_app --> notification_db",
            "  notification_app --> message_queue",
            "  email_app --> message_queue",
            "  sms_app --> message_queue",
            "  push_app --> message_queue",
            "}",
            "@enduml",
        ]
        filename = "notification_module_component_detail.puml"
        (self.output_dir / filename).write_text("\n".join(content))
        return filename

    def generate_dashboard_module_component(self):
        content = [
            "@startuml",
            "package dashboard_module {",
            "  component dashboard_academic_app",
            "  component dashboard_academic_secretary_app",
            "  component dashboard_admin_app",
            "  component dashboard_alumni_app",
            "  component dashboard_collection_agent_app",
            "  component dashboard_doyen_app",
            "  component dashboard_quality_director_app",
            "  component dashboard_recteur_app",
            "  component dashboard_shared_app",
            "  component dashboard_student_app",
            "  component dashboard_student_services_app",
            "  component dashboard_super_admin_app",
            "  component dashboard_teacher_app",
            "}",
            "@enduml",
        ]
        filename = "dashboard_module_component_detail.puml"
        (self.output_dir / filename).write_text("\n".join(content))
        return filename

    def generate_user_role_module_component(self):
        content = [
            "@startuml",
            "package auth_module {",
            "  component user_app {",
            "    [User Management]",
            "    [Profile Management]",
            "    [User Validation]",
            "  }",
            "  ",
            "  component role_app {",
            "    [Role Management]",
            "    [Permission Management]",
            "    [Access Control]",
            "  }",
            "  ",
            "  component authentication_app {",
            "    [Login Service]",
            "    [Registration Service]",
            "    [Token Service]",
            "    [2FA Service]",
            "    [Password Reset]",
            "  }",
            "  ",
            "  component authorization_app {",
            "    [Permission Check]",
            "    [Role Validation]",
            "    [Access Guard]",
            "  }",
            "  ",
            "  database auth_db",
            "  cache token_cache",
            "  ",
            "  user_app --> auth_db",
            "  role_app --> auth_db",
            "  authentication_app --> auth_db",
            "  authentication_app --> token_cache",
            "  authorization_app --> role_app",
            "  ",
            "  authentication_app --> user_app",
            "  authorization_app --> authentication_app",
            "}",
            "@enduml",
        ]
        filename = "user_role_module_component_detail.puml"
        (self.output_dir / filename).write_text("\n".join(content))
        return filename

    def generate_security_module_component(self):
        content = [
            "@startuml",
            "package security_module {",
            "  component audit_app {",
            "    [Audit Logging]",
            "    [Security Event Tracking]",
            "    [Compliance Monitoring]",
            "  }",
            "  ",
            "  component access_control_app {",
            "    [Access Policy Management]",
            "    [Permission Enforcement]",
            "    [Role-Based Access Control]",
            "  }",
            "  ",
            "  component encryption_app {",
            "    [Data Encryption]",
            "    [Key Management]",
            "    [Secure Storage]",
            "  }",
            "  ",
            "  component threat_detection_app {",
            "    [Intrusion Detection]",
            "    [Anomaly Detection]",
            "    [Security Alerts]",
            "  }",
            "  ",
            "  database security_db",
            "  storage secure_vault",
            "  ",
            "  audit_app --> security_db",
            "  access_control_app --> security_db",
            "  encryption_app --> secure_vault",
            "  threat_detection_app --> security_db",
            "  ",
            "  threat_detection_app --> audit_app",
            "  access_control_app --> audit_app",
            "}",
            "@enduml",
        ]
        filename = "security_module_component_detail.puml"
        (self.output_dir / filename).write_text("\n".join(content))
        return filename

    def generate_all(self):
        generated = []
        generated.append(self.generate_academic_module_component())
        generated.append(self.generate_financial_module_component())
        generated.append(self.generate_scheduling_module_component())
        generated.append(self.generate_notification_module_component())
        generated.append(self.generate_dashboard_module_component())
        generated.append(self.generate_user_role_module_component())
        generated.append(self.generate_security_module_component())
        return generated
