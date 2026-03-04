from pathlib import Path

from django.apps import apps


class DatabaseSchemaGenerator:
    """Generate Database Schema Diagrams"""

    def __init__(self, output_dir="docs/diagrams/database"):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)

    def generate_erd(self, module_filter=None):
        """Generate Entity Relationship Diagram"""
        content = ["@startuml", "skinparam linetype ortho", ""]

        for model in apps.get_models():
            if module_filter and module_filter not in model._meta.app_label:
                continue

            table_name = model._meta.db_table
            content.append(f'entity "{table_name}" {{')

            for field in model._meta.get_fields():
                if hasattr(field, "get_internal_type"):
                    field_type = field.get_internal_type()
                    pk = " <<PK>>" if getattr(field, "primary_key", False) else ""
                    fk = " <<FK>>" if getattr(field, "many_to_one", False) else ""
                    content.append(f"  {field.name} : {field_type}{pk}{fk}")

            content.append("}")
            content.append("")

        # Relationships
        for model in apps.get_models():
            if module_filter and module_filter not in model._meta.app_label:
                continue

            for field in model._meta.get_fields():
                if getattr(field, "many_to_one", False) and hasattr(
                    field, "related_model"
                ):
                    left = model._meta.db_table
                    right = field.related_model._meta.db_table
                    content.append(f'"{left}" }}o--|| "{right}"')
                elif getattr(field, "many_to_many", False) and hasattr(
                    field, "related_model"
                ):
                    left = model._meta.db_table
                    right = field.related_model._meta.db_table
                    content.append(f'"{left}" }}o--o{{{{ "{right}"')
                elif getattr(field, "one_to_one", False) and hasattr(
                    field, "related_model"
                ):
                    left = model._meta.db_table
                    right = field.related_model._meta.db_table
                    content.append(f'"{left}" ||--|| "{right}"')

        content.append("@enduml")

        filename = f"erd_{module_filter or 'all'}.puml"
        (self.output_dir / filename).write_text("\n".join(content))
        return filename

    def generate_academic_schema(self):
        """Generate Academic Module Schema"""
        content = [
            "@startuml",
            "skinparam linetype ortho",
            "",
            'entity "university" {',
            "  id : UUID <<PK>>",
            "  university_name : VARCHAR",
            "  university_abrev : VARCHAR",
            "  created_at : TIMESTAMP",
            "}",
            "",
            'entity "faculty" {',
            "  id : UUID <<PK>>",
            "  university_id : UUID <<FK>>",
            "  name : VARCHAR",
            "  code : VARCHAR",
            "}",
            "",
            'entity "department" {',
            "  id : UUID <<PK>>",
            "  faculty_id : UUID <<FK>>",
            "  name : VARCHAR",
            "  code : VARCHAR",
            "}",
            "",
            'entity "program" {',
            "  id : UUID <<PK>>",
            "  department_id : UUID <<FK>>",
            "  name : VARCHAR",
            "  degree_type : VARCHAR",
            "  duration_years : INT",
            "}",
            "",
            'entity "course" {',
            "  id : UUID <<PK>>",
            "  program_id : UUID <<FK>>",
            "  code : VARCHAR",
            "  name : VARCHAR",
            "  credits : INT",
            "}",
            "",
            'entity "class" {',
            "  id : UUID <<PK>>",
            "  program_id : UUID <<FK>>",
            "  academic_year_id : UUID <<FK>>",
            "  name : VARCHAR",
            "  level : INT",
            "}",
            "",
            '"university" ||--o{ "faculty"',
            '"faculty" ||--o{ "department"',
            '"department" ||--o{ "program"',
            '"program" ||--o{ "course"',
            '"program" ||--o{ "class"',
            "",
            "@enduml",
        ]

        filename = "academic_schema.puml"
        (self.output_dir / filename).write_text("\n".join(content))
        return filename

    def generate_student_schema(self):
        """Generate Student Module Schema"""
        content = [
            "@startuml",
            "skinparam linetype ortho",
            "",
            'entity "user" {',
            "  id : UUID <<PK>>",
            "  email : VARCHAR",
            "  role_id : UUID <<FK>>",
            "  university_id : UUID <<FK>>",
            "}",
            "",
            'entity "student" {',
            "  id : UUID <<PK>>",
            "  user_id : UUID <<FK>>",
            "  student_number : VARCHAR",
            "  first_name : VARCHAR",
            "  last_name : VARCHAR",
            "  date_of_birth : DATE",
            "}",
            "",
            'entity "inscription" {',
            "  id : UUID <<PK>>",
            "  student_id : UUID <<FK>>",
            "  class_id : UUID <<FK>>",
            "  academic_year_id : UUID <<FK>>",
            "  status : VARCHAR",
            "}",
            "",
            'entity "grade" {',
            "  id : UUID <<PK>>",
            "  student_id : UUID <<FK>>",
            "  course_id : UUID <<FK>>",
            "  score : DECIMAL",
            "  grade : VARCHAR",
            "}",
            "",
            '"user" ||--|| "student"',
            '"student" ||--o{ "inscription"',
            '"student" ||--o{ "grade"',
            "",
            "@enduml",
        ]

        filename = "student_schema.puml"
        (self.output_dir / filename).write_text("\n".join(content))
        return filename

    def generate_financial_schema(self):
        """Generate Financial Module Schema"""
        content = [
            "@startuml",
            "skinparam linetype ortho",
            "",
            'entity "fee_structure" {',
            "  id : UUID <<PK>>",
            "  program_id : UUID <<FK>>",
            "  academic_year_id : UUID <<FK>>",
            "  amount : DECIMAL",
            "}",
            "",
            'entity "payment_plan" {',
            "  id : UUID <<PK>>",
            "  student_id : UUID <<FK>>",
            "  inscription_id : UUID <<FK>>",
            "  total_amount : DECIMAL",
            "  status : VARCHAR",
            "}",
            "",
            'entity "payment_installment" {',
            "  id : UUID <<PK>>",
            "  payment_plan_id : UUID <<FK>>",
            "  amount : DECIMAL",
            "  due_date : DATE",
            "  paid_amount : DECIMAL",
            "  status : VARCHAR",
            "}",
            "",
            'entity "payment" {',
            "  id : UUID <<PK>>",
            "  installment_id : UUID <<FK>>",
            "  amount : DECIMAL",
            "  payment_date : TIMESTAMP",
            "  payment_method : VARCHAR",
            "}",
            "",
            'entity "derogation" {',
            "  id : UUID <<PK>>",
            "  student_id : UUID <<FK>>",
            "  payment_plan_id : UUID <<FK>>",
            "  amount : DECIMAL",
            "  status : VARCHAR",
            "  approved_by : UUID <<FK>>",
            "}",
            "",
            '"payment_plan" ||--o{ "payment_installment"',
            '"payment_installment" ||--o{ "payment"',
            '"payment_plan" ||--o{ "derogation"',
            "",
            "@enduml",
        ]

        filename = "financial_schema.puml"
        (self.output_dir / filename).write_text("\n".join(content))
        return filename

    def generate_exam_schema(self):
        """Generate Exam Module Schema"""
        content = [
            "@startuml",
            "skinparam linetype ortho",
            "",
            'entity "exam_session" {',
            "  id : UUID <<PK>>",
            "  name : VARCHAR",
            "  academic_year_id : UUID <<FK>>",
            "  start_date : DATE",
            "  end_date : DATE",
            "}",
            "",
            'entity "exam" {',
            "  id : UUID <<PK>>",
            "  exam_session_id : UUID <<FK>>",
            "  course_id : UUID <<FK>>",
            "  exam_date : DATETIME",
            "  duration_minutes : INT",
            "}",
            "",
            'entity "exam_result" {',
            "  id : UUID <<PK>>",
            "  exam_id : UUID <<FK>>",
            "  student_id : UUID <<FK>>",
            "  score : DECIMAL",
            "  grade : VARCHAR",
            "}",
            "",
            '"exam_session" ||--o{ "exam"',
            '"exam" ||--o{ "exam_result"',
            "",
            "@enduml",
        ]

        filename = "exam_schema.puml"
        (self.output_dir / filename).write_text("\n".join(content))
        return filename

    def generate_all(self):
        generated = []
        generated.append(self.generate_erd())
        generated.append(self.generate_academic_schema())
        generated.append(self.generate_student_schema())
        generated.append(self.generate_financial_schema())
        generated.append(self.generate_exam_schema())
        return generated
