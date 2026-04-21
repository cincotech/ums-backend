from pathlib import Path


class TraceabilityMatrixGenerator:
    """Generate Traceability Matrix for Use Cases to Endpoints"""

    def __init__(self, output_dir="docs/diagrams/traceability"):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)

    def generate_matrix(self):
        matrix = {
            "UC1: Manage System Configuration": [
                "GET /api/config/",
                "PUT /api/config/{id}/",
                "POST /api/config/backup/",
            ],
            "UC2: Backup & Restore System": [
                "POST /api/system/backup/",
                "POST /api/system/restore/",
                "GET /api/system/backups/",
            ],
            "UC3: Manage Users & Roles": [
                "GET /api/users/",
                "POST /api/users/",
                "PUT /api/users/{id}/",
                "DELETE /api/users/{id}/",
                "GET /api/roles/",
                "POST /api/roles/",
            ],
            "UC4: Approve Programs": [
                "GET /api/programs/pending/",
                "POST /api/programs/{id}/approve/",
                "POST /api/programs/{id}/reject/",
            ],
            "UC5: Review Academic Programs": [
                "GET /api/programs/",
                "GET /api/programs/{id}/",
                "POST /api/programs/{id}/review/",
            ],
            "UC6: Quality Audit & Compliance": [
                "GET /api/quality/audits/",
                "POST /api/quality/audits/",
                "GET /api/quality/compliance/",
            ],
            "UC7: Manage Faculty & Teaching Loads": [
                "GET /api/faculties/",
                "POST /api/faculties/",
                "GET /api/teachers/workload/",
                "PUT /api/teachers/{id}/workload/",
            ],
            "UC8: Manage Courses & Schedules": [
                "GET /api/courses/",
                "POST /api/courses/",
                "PUT /api/courses/{id}/",
                "GET /api/schedules/",
                "POST /api/schedules/",
            ],
            "UC9: Manage Registrations": [
                "GET /api/inscriptions/",
                "POST /api/inscriptions/",
                "PUT /api/inscriptions/{id}/",
                "GET /api/inscriptions/{id}/status/",
            ],
            "UC10: Manage Documents": [
                "GET /api/documents/requests/",
                "POST /api/documents/requests/",
                "PUT /api/documents/requests/{id}/approve/",
                "GET /api/documents/{id}/download/",
            ],
            "UC11: Manage Payments & Fees": [
                "GET /api/payments/",
                "POST /api/payments/",
                "GET /api/payments/plans/",
                "POST /api/payments/plans/",
                "GET /api/fees/",
            ],
            "UC12: Oversee Academic Affairs": [
                "GET /api/academic/overview/",
                "GET /api/academic/programs/",
                "GET /api/academic/reports/",
            ],
            "UC13: Submit Grades": [
                "GET /api/grades/",
                "POST /api/grades/",
                "PUT /api/grades/{id}/",
                "POST /api/grades/bulk/",
            ],
            "UC14: Record Attendance": [
                "GET /api/attendance/",
                "POST /api/attendance/",
                "PUT /api/attendance/{id}/",
                "GET /api/attendance/report/",
            ],
            "UC15: Mentor Students": [
                "GET /api/counseling/sessions/",
                "POST /api/counseling/sessions/",
                "GET /api/students/{id}/progress/",
            ],
            "UC16: Register Courses": [
                "GET /api/courses/available/",
                "POST /api/students/courses/register/",
                "GET /api/students/courses/",
            ],
            "UC17: View Grades": [
                "GET /api/students/grades/",
                "GET /api/students/transcript/",
            ],
            "UC18: Request Documents": [
                "POST /api/documents/requests/",
                "GET /api/documents/requests/my/",
                "GET /api/documents/{id}/status/",
            ],
            "UC19: Access Alumni Portal": [
                "GET /api/alumni/profile/",
                "PUT /api/alumni/profile/",
                "GET /api/alumni/events/",
            ],
            "UC20: Post Alumni Events/Jobs": [
                "POST /api/alumni/events/",
                "POST /api/alumni/jobs/",
                "GET /api/alumni/jobs/",
            ],
            "UC21: Represent Class & Communicate": [
                "GET /api/class/{id}/students/",
                "POST /api/class/announcements/",
                "GET /api/class/issues/",
            ],
            "UC22: Administrative Support": [
                "GET /api/admin/tasks/",
                "POST /api/admin/support/",
                "GET /api/admin/reports/",
            ],
        }

        # Generate Markdown
        md_content = ["# Traceability Matrix: Use Cases to Endpoints", ""]
        md_content.append("| Use Case | Endpoints |")
        md_content.append("|----------|-----------|")

        for use_case, endpoints in matrix.items():
            endpoints_str = "<br>".join(endpoints)
            md_content.append(f"| {use_case} | {endpoints_str} |")

        md_filename = "traceability_matrix.md"
        (self.output_dir / md_filename).write_text("\n".join(md_content))

        # Generate CSV
        csv_content = ["Use Case,Endpoint"]
        for use_case, endpoints in matrix.items():
            for endpoint in endpoints:
                csv_content.append(f'"{use_case}","{endpoint}"')

        csv_filename = "traceability_matrix.csv"
        (self.output_dir / csv_filename).write_text("\n".join(csv_content))

        # Generate PlantUML
        puml_content = ["@startuml", ""]
        for use_case, endpoints in matrix.items():
            uc_id = use_case.split(":")[0].replace(" ", "")
            puml_content.append(f'usecase "{use_case}" as {uc_id}')
            for endpoint in endpoints:
                endpoint_id = (
                    endpoint.replace("/", "_")
                    .replace("{", "")
                    .replace("}", "")
                    .replace(" ", "")
                )
                puml_content.append(f'rectangle "{endpoint}" as {endpoint_id}')
                puml_content.append(f"{uc_id} --> {endpoint_id}")
            puml_content.append("")

        puml_content.append("@enduml")
        puml_filename = "traceability_matrix.puml"
        (self.output_dir / puml_filename).write_text("\n".join(puml_content))

        return [md_filename, csv_filename, puml_filename]
