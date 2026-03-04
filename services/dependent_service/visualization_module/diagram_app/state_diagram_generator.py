from pathlib import Path


class StateDiagramGenerator:
    """Generate PlantUML State Diagrams"""

    def __init__(self, output_dir="docs/diagrams/plantuml/states"):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)

    def generate_student_state(self):
        content = [
            "@startuml",
            "[*] --> Applicant",
            "Applicant --> Registered : Application Approved",
            "Registered --> Active : Inscription Complete",
            "Active --> Suspended : Disciplinary Action",
            "Suspended --> Active : Suspension Lifted",
            "Active --> Graduated : Completed Program",
            "Active --> Withdrawn : Voluntary Withdrawal",
            "Graduated --> Alumni",
            "Alumni --> [*]",
            "Withdrawn --> [*]",
            "@enduml",
        ]
        filename = "student_state.puml"
        (self.output_dir / filename).write_text("\n".join(content))
        return filename

    def generate_payment_state(self):
        content = [
            "@startuml",
            "[*] --> Pending",
            "Pending --> PartiallyPaid : Partial Payment",
            "Pending --> Paid : Full Payment",
            "PartiallyPaid --> Paid : Remaining Payment",
            "Paid --> [*]",
            "Pending --> Overdue : Deadline Passed",
            "PartiallyPaid --> Overdue : Deadline Passed",
            "Overdue --> Paid : Late Payment",
            "@enduml",
        ]
        filename = "payment_state.puml"
        (self.output_dir / filename).write_text("\n".join(content))
        return filename

    def generate_course_state(self):
        content = [
            "@startuml",
            "[*] --> Draft",
            "Draft --> Pending : Submit for Approval",
            "Pending --> Approved : Dean Approves",
            "Pending --> Rejected : Dean Rejects",
            "Rejected --> Draft : Revise",
            "Approved --> Active : Semester Starts",
            "Active --> Completed : Semester Ends",
            "Completed --> [*]",
            "@enduml",
        ]
        filename = "course_state.puml"
        (self.output_dir / filename).write_text("\n".join(content))
        return filename

    def generate_exam_state(self):
        content = [
            "@startuml",
            "[*] --> Scheduled",
            "Scheduled --> InProgress : Exam Starts",
            "InProgress --> Grading : Exam Ends",
            "Grading --> Graded : All Grades Submitted",
            "Graded --> Published : Results Published",
            "Published --> [*]",
            "@enduml",
        ]
        filename = "exam_state.puml"
        (self.output_dir / filename).write_text("\n".join(content))
        return filename

    def generate_document_request_state(self):
        content = [
            "@startuml",
            "[*] --> Requested",
            "Requested --> InReview : Service Reviews",
            "InReview --> Approved : Approved",
            "InReview --> Rejected : Rejected",
            "Approved --> Generated : Document Generated",
            "Generated --> Delivered : Delivered to Student",
            "Delivered --> [*]",
            "Rejected --> [*]",
            "@enduml",
        ]
        filename = "document_request_state.puml"
        (self.output_dir / filename).write_text("\n".join(content))
        return filename

    def generate_inscription_state(self):
        content = [
            "@startuml",
            "[*] --> Initiated",
            "Initiated --> DocumentsSubmitted : Documents Uploaded",
            "DocumentsSubmitted --> Validated : Documents Verified",
            "Validated --> PaymentPending : Awaiting Payment",
            "PaymentPending --> Confirmed : Payment Received",
            "Confirmed --> [*]",
            "DocumentsSubmitted --> Rejected : Invalid Documents",
            "Rejected --> [*]",
            "@enduml",
        ]
        filename = "inscription_state.puml"
        (self.output_dir / filename).write_text("\n".join(content))
        return filename

    def generate_derogation_state(self):
        content = [
            "@startuml",
            "[*] --> Requested",
            "Requested --> UnderReview : Finance Reviews",
            "UnderReview --> RectorReview : Forwarded to Rector",
            "RectorReview --> Approved : Rector Approves",
            "RectorReview --> Rejected : Rector Rejects",
            "Approved --> Applied : Applied to Payment Plan",
            "Applied --> [*]",
            "Rejected --> [*]",
            "@enduml",
        ]
        filename = "derogation_state.puml"
        (self.output_dir / filename).write_text("\n".join(content))
        return filename

    def generate_program_state(self):
        content = [
            "@startuml",
            "[*] --> Draft",
            "Draft --> DeanReview : Submitted by Dean",
            "DeanReview --> AcademicDirectorReview : Dean Approves",
            "AcademicDirectorReview --> QualityReview : Academic Director Approves",
            "QualityReview --> RectorReview : Quality Director Approves",
            "RectorReview --> Approved : Rector Approves",
            "Approved --> Active : Published",
            "Active --> [*]",
            "DeanReview --> Draft : Rejected",
            "AcademicDirectorReview --> Draft : Rejected",
            "QualityReview --> Draft : Rejected",
            "RectorReview --> Draft : Rejected",
            "@enduml",
        ]
        filename = "program_state.puml"
        (self.output_dir / filename).write_text("\n".join(content))
        return filename

    def generate_all(self):
        generated = []
        generated.append(self.generate_student_state())
        generated.append(self.generate_payment_state())
        generated.append(self.generate_course_state())
        generated.append(self.generate_exam_state())
        generated.append(self.generate_document_request_state())
        generated.append(self.generate_inscription_state())
        generated.append(self.generate_derogation_state())
        generated.append(self.generate_program_state())
        return generated
