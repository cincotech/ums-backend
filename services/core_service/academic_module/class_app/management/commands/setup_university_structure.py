#!/usr/bin/env python3
from django.core.management.base import BaseCommand
from django.db import transaction
from django.utils import timezone
from faker import Faker
from random import choice, sample

# Import your models
from services.core_service.academic_module.class_app.models import Class, ClassGroup
from services.core_service.academic_module.teacher_app.models import Teacher, Attribution
from services.core_service.academic_module.course_app.models import Course
from services.core_service.academic_module.faculty_app.models import Faculty
from services.core_service.academic_module.university_app.models import AcademicYear, UniversityDegree, University
from services.foundational_service.auth_module.user_app.models import User, Role
from services.foundational_service.auth_module.authorization_app.models import Profile
from services.dependent_service.scheduling_module.scheduling_app.models import Timetable, ScheduleSlot
from services.dependent_service.infrastructure_module.room_app.models import Room

from dateutil.relativedelta import relativedelta

class Command(BaseCommand):
    help = 'Create class groups, teachers, deans, and timetables'

    def add_arguments(self, parser):
        parser.add_argument('--academic-year-id', type=str, help='Academic year UUID')

    def handle(self, *args, **options):
        fake = Faker()
        academic_year_id = options.get('academic_year_id')

        # Get academic year
        if academic_year_id:
            try:
                academic_year = AcademicYear.objects.get(id=academic_year_id)
            except AcademicYear.DoesNotExist:
                self.stdout.write(self.style.ERROR('Academic year not found'))
                return
        else:
            academic_year = AcademicYear.objects.filter(is_closed=False).first()
            if not academic_year:
                self.stdout.write(self.style.ERROR('No active academic year found'))
                return

        # Get roles
        try:
            teacher_role = Role.objects.get(name='teacher')
            dean_role = Role.objects.get(name='dean')
        except Role.DoesNotExist as e:
            self.stdout.write(self.style.ERROR(f'Role not found: {e}'))
            return

        classes = Class.objects.all()
        rooms = list(Room.objects.all())
        slots = list(ScheduleSlot.objects.all())
        degrees = list(UniversityDegree.objects.all())
        university = University.objects.first()

        # Validate required data
        if not classes.exists():
            self.stdout.write(self.style.ERROR('No classes found'))
            return
        if not rooms:
            self.stdout.write(self.style.ERROR('No rooms found'))
            return
        if not slots:
            self.stdout.write(self.style.ERROR('No schedule slots found'))
            return
        if not degrees:
            # Create default degrees
            degrees = [
                UniversityDegree.objects.get_or_create(degree_name=name)[0]
                for name in ['Bachelor', 'Master', 'PhD', 'Diploma']
            ]
            self.stdout.write(self.style.SUCCESS('Created default degrees'))
        if not university:
            self.stdout.write(self.style.ERROR('No university found'))
            return

        with transaction.atomic():
            # -------------------
            # Create 20 teachers
            # -------------------
            self.stdout.write('Creating 20 teachers...')
            teachers = []
            for _ in range(20):
                user, _ = User.objects.get_or_create(
                    email=fake.unique.email(),
                    defaults={
                        'first_name': fake.first_name(),
                        'last_name': fake.last_name(),
                        'phone_number': fake.phone_number()[:20],
                        'role': teacher_role,
                        'gender': choice(['M', 'F']),
                        'birth_date': fake.date_of_birth(minimum_age=30, maximum_age=65),
                        'email_verified': True
                    }
                )
                user.set_password('password123')
                user.save()

                teacher = Teacher.objects.create(
                    user=user,
                    teacher_grade=choice(['Assistant', 'Lecturer', 'Professor']),
                    degree=choice(degrees),
                    university=university
                )
                teachers.append(teacher)

            self.stdout.write(self.style.SUCCESS(f'Created {len(teachers)} teachers'))

            # -------------------
            # Create deans
            # -------------------
            self.stdout.write('Creating deans for each faculty...')
            faculties = Faculty.objects.all()
            for faculty in faculties:
                user, _ = User.objects.get_or_create(
                    email=f"dean.{faculty.faculty_abreviation.lower()}@university.edu",
                    defaults={
                        'first_name': fake.first_name(),
                        'last_name': fake.last_name(),
                        'phone_number': fake.phone_number()[:20],
                        'role': dean_role,
                        'gender': choice(['M', 'F']),
                        'birth_date': fake.date_of_birth(minimum_age=40, maximum_age=65),
                        'email_verified': True
                    }
                )
                user.set_password('password123')
                user.save()

                Profile.objects.create(
                    user=user,
                    faculty=faculty,
                    start_date=fake.date_between(start_date='-2y', end_date='today')
                )
                self.stdout.write(self.style.SUCCESS(f'Created dean for {faculty.faculty_name}'))

            # -------------------
            # Create class groups
            # -------------------
            self.stdout.write('Creating class groups...')
            total_groups = 0
            for class_obj in classes:
                for i in range(1, 2):
                    ClassGroup.objects.get_or_create(
                        class_fk=class_obj,
                        academic_year=academic_year,
                        group_name=f"G{i}"
                    )
                    total_groups += 1
            self.stdout.write(self.style.SUCCESS(f'Created {total_groups} class groups'))

            self.stdout.write('Creating attributions and timetables...')
            total_timetables = 0

            for class_obj in classes:
                courses = Course.objects.filter(module__class_fk=class_obj)
                class_groups = ClassGroup.objects.filter(class_fk=class_obj, academic_year=academic_year)
                
                for course in courses:
                    teacher = choice(teachers)
                    attribution, _ = Attribution.objects.get_or_create(
                        course=course,
                        principal_teacher=teacher,
                        academic_year=academic_year,
                        submitted_by=teacher.user,
                        defaults={
                            'status_principal_teacher': 'Accepted',
                            'date_attribution': timezone.now().date()
                        }
                    )

                    for group in class_groups:
                        # Track used (room_id, start_date, end_date) for this class group
                        used_combinations = set()
                        
                        for _ in range(1):  # 3 timetables per group
                            max_attempts = 20
                            for attempt in range(max_attempts):
                                generated_start = fake.date_between(start_date='today', end_date='+30d')
                                generated_end = generated_start + relativedelta(months=12)
                                selected_room = choice(rooms)

                                key = (group.id, selected_room.id, generated_start, generated_end)
                                if key not in used_combinations:
                                    # This combination is safe
                                    used_combinations.add(key)
                                    break
                            else:
                                # Could not find a unique combination after 20 tries
                                print(f"Skipping timetable creation for group {group.id} due to repeated conflicts.")
                                continue

                            # Create timetable
                            timetable = Timetable.objects.create(
                                class_group=group,
                                attribution=attribution,
                                room=selected_room,
                                start_date=generated_start,
                                end_date=generated_end,
                                created_by=teacher.user
                            )
                            timetable.slots.set(sample(slots, min(3, len(slots))))
                            total_timetables += 1


            self.stdout.write(self.style.SUCCESS(f'Created {total_timetables} timetables'))
            self.stdout.write(self.style.SUCCESS('Successfully completed setup!'))
