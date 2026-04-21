from pathlib import Path


class PackageDiagramGenerator:
    """Generate PlantUML Package Diagrams"""

    def __init__(self, output_dir="docs/diagrams/plantuml/packages"):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)

    def generate_academic_module_package(self):
        content = [
            "@startuml",
            "package academic_module {",
            "  package university_app {",
            "    class University",
            "    class Faculty",
            "    class Department",
            "  }",
            "  package program_app {",
            "    class Program",
            "    class Course",
            "    class Curriculum",
            "  }",
            "  package class_app {",
            "    class Class",
            "    class ClassRoom",
            "    class AcademicYear",
            "  }",
            "  package result_app {",
            "    class Grade",
            "    class Transcript",
            "  }",
            "}",
            "@enduml",
        ]
        filename = "academic_module_package.puml"
        (self.output_dir / filename).write_text("\n".join(content))
        return filename

    def generate_financial_module_package(self):
        content = [
            "@startuml",
            "package financial_module {",
            "  package payment_app {",
            "    class Payment",
            "    class PaymentPlan",
            "    class PaymentInstallment",
            "  }",
            "  package fee_app {",
            "    class FeeStructure",
            "    class FeeCategory",
            "  }",
            "  package derogation_app {",
            "    class Derogation",
            "    class DerogationRequest",
            "  }",
            "  package scholarship_app {",
            "    class Scholarship",
            "    class ScholarshipApplication",
            "  }",
            "}",
            "@enduml",
        ]
        filename = "financial_module_package.puml"
        (self.output_dir / filename).write_text("\n".join(content))
        return filename

    def generate_scheduling_module_package(self):
        content = [
            "@startuml",
            "package scheduling_module {",
            "  package schedule_app {",
            "    class Schedule",
            "    class TimeSlot",
            "    class ClassSession",
            "  }",
            "  package timetable_app {",
            "    class Timetable",
            "    class TimetableEntry",
            "  }",
            "  package attendance_app {",
            "    class Attendance",
            "    class AttendanceRecord",
            "  }",
            "}",
            "@enduml",
        ]
        filename = "scheduling_module_package.puml"
        (self.output_dir / filename).write_text("\n".join(content))
        return filename

    def generate_notification_module_package(self):
        content = [
            "@startuml",
            "package notification_module {",
            "  package notification_app {",
            "    class Notification",
            "    class NotificationTemplate",
            "  }",
            "  package email_app {",
            "    class EmailService",
            "    class EmailQueue",
            "  }",
            "  package sms_app {",
            "    class SMSService",
            "    class SMSQueue",
            "  }",
            "}",
            "@enduml",
        ]
        filename = "notification_module_package.puml"
        (self.output_dir / filename).write_text("\n".join(content))
        return filename

    def generate_dashboard_module_package(self):
        content = [
            "@startuml",
            "package dashboard_module {",
            "  package analytics_app {",
            "    class Analytics",
            "    class Report",
            "  }",
            "  package metrics_app {",
            "    class Metric",
            "    class KPI",
            "  }",
            "  package visualization_app {",
            "    class Chart",
            "    class Dashboard",
            "  }",
            "}",
            "@enduml",
        ]
        filename = "dashboard_module_package.puml"
        (self.output_dir / filename).write_text("\n".join(content))
        return filename

    def generate_user_role_module_package(self):
        content = [
            "@startuml",
            "package auth_module {",
            "  package user_app {",
            "    class User",
            "    class Profile",
            "  }",
            "  package role_app {",
            "    class Role",
            "    class Permission",
            "  }",
            "  package authentication_app {",
            "    class AuthService",
            "    class TokenService",
            "  }",
            "}",
            "@enduml",
        ]
        filename = "user_role_module_package.puml"
        (self.output_dir / filename).write_text("\n".join(content))
        return filename

    def generate_security_module_package(self):
        content = [
            "@startuml",
            "package security_module {",
            "  package audit_app {",
            "    class AuditLog",
            "    class SecurityEvent",
            "  }",
            "  package access_control_app {",
            "    class AccessControl",
            "    class RolePermission",
            "  }",
            "  package encryption_app {",
            "    class EncryptionService",
            "    class KeyManagement",
            "  }",
            "}",
            "@enduml",
        ]
        filename = "security_module_package.puml"
        (self.output_dir / filename).write_text("\n".join(content))
        return filename

    def generate_all_modules_package(self):
        content = [
            "@startuml",
            "package foundational_service {",
            "  package geo_module",
            "  package auth_module",
            "}",
            "",
            "package core_service {",
            "  package academic_module",
            "  package student_module",
            "}",
            "",
            "package dependent_service {",
            "  package document_module",
            "  package exam_module",
            "  package infrastructure_module",
            "  package notification_module",
            "  package scheduling_module",
            "  package dashboard_module",
            "  package financial_module",
            "}",
            "",
            "foundational_service --> core_service",
            "core_service --> dependent_service",
            "@enduml",
        ]
        filename = "all_modules_package.puml"
        (self.output_dir / filename).write_text("\n".join(content))
        return filename

    def generate_all(self):
        generated = []
        generated.append(self.generate_academic_module_package())
        generated.append(self.generate_financial_module_package())
        generated.append(self.generate_scheduling_module_package())
        generated.append(self.generate_notification_module_package())
        generated.append(self.generate_dashboard_module_package())
        generated.append(self.generate_user_role_module_package())
        generated.append(self.generate_security_module_package())
        generated.append(self.generate_all_modules_package())
        return generated
