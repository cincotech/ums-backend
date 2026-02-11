from django.core.management.base import BaseCommand

from services.core_service.academic_module.survey_app.models import Question, Survey
from services.foundational_service.auth_module.user_app.models import User


class Command(BaseCommand):
    help = "Create sample survey data for testing"

    def handle(self, *args, **options):
        self.stdout.write(self.style.WARNING("Creating sample survey data..."))

        # Get or create admin user
        admin_user = User.objects.filter(is_superuser=True).first()
        if not admin_user:
            self.stdout.write(
                self.style.ERROR("No admin user found. Please create one first.")
            )
            return

        # Create Student Satisfaction Survey
        survey1, created = Survey.objects.get_or_create(
            title="Student Satisfaction Survey",
            defaults={
                "description": "Help us improve your learning experience",
                "multi_step": True,
                "created_by": admin_user,
            },
        )

        if created:
            questions_data = [
                {
                    "label": "What is your name?",
                    "type": "text",
                    "required": True,
                    "section": "Personal Info",
                    "order": 1,
                },
                {
                    "label": "Your email address",
                    "type": "email",
                    "required": True,
                    "section": "Personal Info",
                    "order": 2,
                },
                {
                    "label": "Which program are you enrolled in?",
                    "type": "select",
                    "required": True,
                    "section": "Academic",
                    "order": 3,
                    "options": [
                        "Computer Science",
                        "Engineering",
                        "Business",
                        "Medicine",
                        "Law",
                    ],
                },
                {
                    "label": "Rate the quality of teaching",
                    "type": "rating",
                    "required": True,
                    "section": "Feedback",
                    "max": 5,
                    "order": 4,
                },
                {
                    "label": "Rate the campus facilities",
                    "type": "rating",
                    "required": True,
                    "section": "Feedback",
                    "max": 5,
                    "order": 5,
                },
                {
                    "label": "Which aspects need improvement?",
                    "type": "checkbox",
                    "section": "Feedback",
                    "order": 6,
                    "options": [
                        "Teaching Quality",
                        "Infrastructure",
                        "Library Resources",
                        "Sports Facilities",
                        "Cafeteria",
                    ],
                },
                {
                    "label": "Additional comments or suggestions",
                    "type": "textarea",
                    "section": "Feedback",
                    "placeholder": "Share your thoughts...",
                    "order": 7,
                },
            ]

            for q_data in questions_data:
                Question.objects.create(survey=survey1, **q_data)

            self.stdout.write(self.style.SUCCESS(f"✓ Created survey: {survey1.title}"))

        # Create Course Evaluation Survey
        survey2, created = Survey.objects.get_or_create(
            title="Course Evaluation",
            defaults={
                "description": "Evaluate your course experience",
                "multi_step": False,
                "created_by": admin_user,
            },
        )

        if created:
            questions_data = [
                {
                    "label": "Course name",
                    "type": "text",
                    "required": True,
                    "section": "default",
                    "order": 1,
                },
                {
                    "label": "Instructor name",
                    "type": "text",
                    "required": True,
                    "section": "default",
                    "order": 2,
                },
                {
                    "label": "Rate the course content",
                    "type": "rating",
                    "required": True,
                    "section": "default",
                    "max": 5,
                    "order": 3,
                },
                {
                    "label": "Rate the instructor effectiveness",
                    "type": "rating",
                    "required": True,
                    "section": "default",
                    "max": 5,
                    "order": 4,
                },
                {
                    "label": "Would you recommend this course?",
                    "type": "radio",
                    "required": True,
                    "section": "default",
                    "order": 5,
                    "options": ["Yes", "No", "Maybe"],
                },
                {
                    "label": "What did you like most?",
                    "type": "textarea",
                    "section": "default",
                    "order": 6,
                },
            ]

            for q_data in questions_data:
                Question.objects.create(survey=survey2, **q_data)

            self.stdout.write(self.style.SUCCESS(f"✓ Created survey: {survey2.title}"))

        # Create Campus Feedback Survey
        survey3, created = Survey.objects.get_or_create(
            title="Campus Feedback",
            defaults={
                "description": "Share your campus experience",
                "multi_step": False,
                "created_by": admin_user,
            },
        )

        if created:
            questions_data = [
                {
                    "label": "Your student ID",
                    "type": "text",
                    "required": True,
                    "section": "default",
                    "order": 1,
                },
                {
                    "label": "Year of study",
                    "type": "select",
                    "required": True,
                    "section": "default",
                    "order": 2,
                    "options": [
                        "1st Year",
                        "2nd Year",
                        "3rd Year",
                        "4th Year",
                        "Graduate",
                    ],
                },
                {
                    "label": "Rate campus safety",
                    "type": "rating",
                    "required": True,
                    "section": "default",
                    "max": 5,
                    "order": 3,
                },
                {
                    "label": "Rate internet connectivity",
                    "type": "rating",
                    "required": True,
                    "section": "default",
                    "max": 5,
                    "order": 4,
                },
                {
                    "label": "Which services do you use regularly?",
                    "type": "checkbox",
                    "section": "default",
                    "order": 5,
                    "options": [
                        "Library",
                        "Cafeteria",
                        "Sports Center",
                        "Computer Lab",
                        "Study Rooms",
                    ],
                },
                {
                    "label": "Suggestions for improvement",
                    "type": "textarea",
                    "section": "default",
                    "placeholder": "Your suggestions...",
                    "order": 6,
                },
            ]

            for q_data in questions_data:
                Question.objects.create(survey=survey3, **q_data)

            self.stdout.write(self.style.SUCCESS(f"✓ Created survey: {survey3.title}"))

        self.stdout.write(
            self.style.SUCCESS("\n✓ Sample survey data created successfully!")
        )
        self.stdout.write(
            self.style.SUCCESS(f"Total surveys: {Survey.objects.count()}")
        )
        self.stdout.write(
            self.style.SUCCESS(f"Total questions: {Question.objects.count()}")
        )
