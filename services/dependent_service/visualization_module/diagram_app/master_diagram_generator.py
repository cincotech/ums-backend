from .component_detail_generator import ComponentDetailGenerator
from .database_schema_generator import DatabaseSchemaGenerator
from .package_diagram_generator import PackageDiagramGenerator
from .plantuml_generator import PlantUMLGenerator
from .state_diagram_generator import StateDiagramGenerator
from .traceability_matrix_generator import TraceabilityMatrixGenerator


class MasterDiagramGenerator:
    """Master generator to orchestrate all diagram generation"""

    def __init__(self, base_output_dir="docs/diagrams"):
        self.base_output_dir = base_output_dir
        self.plantuml_gen = PlantUMLGenerator()
        self.state_gen = StateDiagramGenerator()
        self.package_gen = PackageDiagramGenerator()
        self.traceability_gen = TraceabilityMatrixGenerator()
        self.db_schema_gen = DatabaseSchemaGenerator()
        self.component_detail_gen = ComponentDetailGenerator()

    def generate_all_diagrams(self):
        """Generate all diagrams for the UMS system"""
        results = {
            "plantuml": [],
            "state": [],
            "package": [],
            "traceability": [],
            "database": [],
            "component_detail": [],
        }

        print("Generating PlantUML diagrams...")
        results["plantuml"] = self.plantuml_gen.generate_all()

        print("Generating State diagrams...")
        results["state"] = self.state_gen.generate_all()

        print("Generating Package diagrams...")
        results["package"] = self.package_gen.generate_all()

        print("Generating Traceability matrix...")
        results["traceability"] = self.traceability_gen.generate_matrix()

        print("Generating Database schema diagrams...")
        results["database"] = self.db_schema_gen.generate_all()

        print("Generating Component detail diagrams...")
        results["component_detail"] = self.component_detail_gen.generate_all()

        return results

    def generate_module_specific(self, module_name):
        """Generate diagrams for a specific module"""
        results = {}

        print(f"Generating diagrams for {module_name}...")
        results["class"] = self.plantuml_gen.generate_class_diagram(module_name)
        results["object"] = self.plantuml_gen.generate_object_diagram(module_name)
        results["erd"] = self.db_schema_gen.generate_erd(module_name)

        return results

    def generate_activity_diagrams_by_category(self):
        """Generate all activity diagrams organized by category"""
        categories = {
            "auth": ["auth_login", "auth_register", "auth_password_reset"],
            "student": [
                "student_enrollment",
                "student_course_registration",
                "student_document_request",
            ],
            "teacher": ["teacher_grade_submission", "teacher_attendance"],
            "dean": ["dean_course_management", "dean_faculty_management"],
            "rector": ["rector_payment_derogation", "rector_program_approval"],
            "quality": ["quality_audit", "quality_satisfaction_survey"],
            "financial": ["payment_collection", "payment_plan_creation"],
            "student_service": [
                "student_service_scholarship",
                "student_service_counseling",
            ],
            "alumni": ["alumni_event", "alumni_job_posting"],
            "secretary": ["secretary_schedule_management"],
            "super_admin": ["super_admin_config", "super_admin_university_setup"],
            "academic_director": ["academic_director_program_review"],
            "exam": ["exam_session_creation"],
            "document": ["document_generation"],
        }

        results = {}
        for category, processes in categories.items():
            results[category] = []
            for process in processes:
                filename = self.plantuml_gen.generate_activity_diagram(process)
                results[category].append(filename)

        return results

    def generate_sequence_diagrams_all(self):
        """Generate all sequence diagrams"""
        scenarios = [
            "student_registration",
            "grade_submission",
            "auth_login_flow",
            "student_inscription_flow",
            "dashboard_notifications_flow",
            "dashboard_payment_collection_flow",
        ]

        results = []
        for scenario in scenarios:
            filename = self.plantuml_gen.generate_sequence_diagram(scenario)
            results.append(filename)

        return results

    def generate_summary_report(self, results):
        """Generate a summary report of all generated diagrams"""
        report = ["# UMS Diagram Generation Report", "", "## Summary", ""]

        total_count = 0
        for category, files in results.items():
            count = len(files) if isinstance(files, list) else 1
            total_count += count
            report.append(f"- {category.title()}: {count} diagrams")

        report.append(f"\n**Total Diagrams Generated: {total_count}**")
        report.append("\n## Details\n")

        for category, files in results.items():
            report.append(f"### {category.title()}")
            if isinstance(files, list):
                for file in files:
                    report.append(f"- {file}")
            else:
                report.append(f"- {files}")
            report.append("")

        return "\n".join(report)
