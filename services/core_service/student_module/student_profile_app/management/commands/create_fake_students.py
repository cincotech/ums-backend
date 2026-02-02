import random

from django.core.management.base import BaseCommand
from django.db import transaction
from faker import Faker

from services.core_service.academic_module.class_app.models import Class
from services.core_service.academic_module.university_app.models import AcademicYear
from services.core_service.student_module.inscription_app.models import Inscription
from services.core_service.student_module.parent_app.models import Parent, Profession
from services.core_service.student_module.student_profile_app.models import Student
from services.foundational_service.auth_module.user_app.models import Role, User
from services.foundational_service.geo_module.colline_app.models import Colline


class Command(BaseCommand):
    help = "Create fake students with inscriptions for each class"

    def add_arguments(self, parser):
        parser.add_argument(
            "--students-per-class",
            type=int,
            default=10,
            help="Number of students per class",
        )
        parser.add_argument("--academic-year-id", type=str, help="Academic year UUID")

    def handle(self, *args, **options):
        fake = Faker()
        students_per_class = options["students_per_class"]
        academic_year_id = options.get("academic_year_id")

        if academic_year_id:
            academic_year = AcademicYear.objects.get(id=academic_year_id)
        else:
            academic_year = AcademicYear.objects.filter(is_closed=False).first()
            if not academic_year:
                self.stdout.write(self.style.ERROR("No active academic year found"))
                return

        student_role = Role.objects.get(name="student")
        classes = Class.objects.all()
        collines = list(Colline.objects.all())
        professions = list(Profession.objects.all())

        if not classes.exists():
            self.stdout.write(self.style.ERROR("No classes found"))
            return

        if not collines:
            self.stdout.write(self.style.ERROR("No collines found"))
            return

        if not professions:
            self.stdout.write(self.style.ERROR("No professions found"))
            return

        total_created = 0

        with transaction.atomic():
            for class_obj in classes:
                self.stdout.write(f"Creating students for {class_obj.class_name}...")

                for i in range(students_per_class):

                    user, _ = User.objects.get_or_create(
                        email=fake.unique.email(),
                        first_name=fake.first_name(),
                        last_name=fake.last_name(),
                        phone_number=fake.phone_number()[:20],
                        role=student_role,
                        gender=random.choice(["M", "F", "O"]),
                        marital_status=random.choice(["S", "M", "D", "W"]),
                        birth_date=fake.date_of_birth(minimum_age=18, maximum_age=30),
                        email_verified=True,
                    )
                    user.set_password("password123")
                    user.save()

                    father = Parent.objects.create(
                        parent_name=fake.name_male(),
                        parent_phone=fake.phone_number()[:15],
                        parent_email=fake.email(),
                        profession=random.choice(professions),
                        parent_type="F",
                        is_alive=random.choice([True, False]),
                        is_contact_person=True,
                    )

                    mother = Parent.objects.create(
                        parent_name=fake.name_female(),
                        parent_phone=fake.phone_number()[:15],
                        parent_email=fake.email(),
                        profession=random.choice(professions),
                        parent_type="M",
                        is_alive=random.choice([True, False]),
                        is_contact_person=False,
                    )

                    student = Student.objects.create(
                        user=user,
                        colline=random.choice(collines),
                        cam=random.randint(50, 100),
                    )

                    student.parent.add(father, mother)

                    Inscription.objects.create(
                        student=student,
                        class_fk=class_obj,
                        academic_year=academic_year,
                        regist_status="Active",
                        is_year_close=False,
                        date_inscription=fake.date_between(
                            start_date="-1y", end_date="today"
                        ),
                    )

                    total_created += 1

                self.stdout.write(
                    self.style.SUCCESS(
                        f"Created {students_per_class} students for {class_obj.class_name}"
                    )
                )

        self.stdout.write(
            self.style.SUCCESS(
                f"Successfully created {total_created} students across {classes.count()} classes"
            )
        )
