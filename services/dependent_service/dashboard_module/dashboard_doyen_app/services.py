# from django.db.models import Avg, Count, Sum
# from django.utils import timezone
# from services.core_service.academic_module.faculty_app.models import Faculty
# from services.academic_module.departement_app.models import  Department
# from services.dependedent_service.scheduling_module.scheduling_app.models import Timetable
# from services.core_service.academic_module.class_app.models import   ClassGroup
# from .models import (
#     SecretaryNote,
#     TeacherWorkload,
#     TeachingProgress,
# )


# class DoyenDashboardService:
#     """Service pour gérer le tableau de bord du Doyen"""

#     # ------------------------------
#     # TIMETABLES
#     # ------------------------------
#     @staticmethod
#     def get_faculty_timetables(faculty: Faculty):
#         """Récupérer tous les emplois du temps pour une faculté"""
#         return Timetable.objects.filter(faculty=faculty).order_by("-created_date")

#     @staticmethod
#     def create_timetable(faculty, academic_year, semester, created_by, room=None):
#         """Créer un nouvel emploi du temps"""
#         timetable, created = Timetable.objects.get_or_create(
#             faculty=faculty,
#             academic_year=academic_year,
#             semester=semester,
#             defaults={"created_by": created_by, "room": room},
#         )
#         return timetable

#     @staticmethod
#     def publish_timetable(timetable):
#         """Publier un emploi du temps"""
#         timetable.status = "published"
#         timetable.published_date = timezone.now()
#         timetable.save()
#         return timetable

#     # ------------------------------
#     # TEACHING PROGRESS
#     # ------------------------------
#     @staticmethod
#     def get_teaching_progress(faculty):
#         """Obtenir la progression de tous les enseignements de la faculté"""
#         return TeachingProgress.objects.filter(faculty=faculty).select_related(
#             "attribution", "submitted_by"
#         )

#     @staticmethod
#     def update_teaching_progress(attribution, faculty, progress_percentage, submitted_by):
#         """Créer ou mettre à jour la progression d'un cours"""
#         progress, created = TeachingProgress.objects.update_or_create(
#             attribution=attribution,
#             faculty=faculty,
#             defaults={
#                 "progress_percentage": progress_percentage,
#                 "submitted_by": submitted_by,
#             },
#         )
#         return progress

#     # ------------------------------
#     # TEACHER WORKLOAD
#     # ------------------------------
#     @staticmethod
#     def get_teacher_workload(faculty, academic_year):
#         """Obtenir la charge horaire des enseignants"""
#         return TeacherWorkload.objects.filter(
#             faculty=faculty, academic_year=academic_year
#         )

#     @staticmethod
#     def update_teacher_workload(faculty, teacher, academic_year, assigned_hours, is_permanent):
#         """Créer ou mettre à jour la charge d'un enseignant"""
#         workload, created = TeacherWorkload.objects.update_or_create(
#             faculty=faculty,
#             teacher=teacher,
#             academic_year=academic_year,
#             defaults={
#                 "assigned_hours": assigned_hours,
#                 "is_permanent": is_permanent,
#             },
#         )
#         return workload

#     # ------------------------------
#     # CLASS / STUDENT GROUPS
#     # ------------------------------
#     @staticmethod
#     def create_class_group(department, group_name, academic_year):
#         """Créer un groupe de classe pour un département"""
#         group = ClassGroup.objects.create(
#             department=department,
#             group_name=group_name,
#             academic_year=academic_year,
#         )
#         return group

#     @staticmethod
#     def add_students_to_class_group(group, students):
#         """Ajouter des étudiants à un groupe de classe"""
#         group.students.add(*students)
#         return group

#     @staticmethod
#     def get_department_class_groups(department):
#         """Obtenir tous les groupes de classe d'un département"""
#         return ClassGroup.objects.filter(department=department)

#     # ------------------------------
#     # DEPARTMENTS
#     # ------------------------------
#     @staticmethod
#     def get_faculty_departments(faculty):
#         """Obtenir tous les départements de la faculté"""
#         return Department.objects.filter(faculty=faculty)

#     # ------------------------------
#     # SECRETARY NOTES
#     # ------------------------------
#     @staticmethod
#     def create_secretary_note(faculty, subject, message, created_by):
#         """Créer une note pour le secrétaire"""
#         note = SecretaryNote.objects.create(
#             faculty=faculty,
#             subject=subject,
#             message=message,
#             created_by=created_by,
#         )
#         return note

#     @staticmethod
#     def resolve_secretary_note(note):
#         """Marquer une note comme résolue"""
#         note.is_resolved = True
#         note.save()
#         return note

#     # ------------------------------
#     # DASHBOARD STATISTICS
#     # ------------------------------
#     @staticmethod
#     def get_dashboard_stats(faculty):
#         """Obtenir les statistiques principales pour le dashboard du Doyen"""
#         timetables = Timetable.objects.filter(faculty=faculty)
#         teaching_progress = TeachingProgress.objects.filter(faculty=faculty)
#         workloads = TeacherWorkload.objects.filter(faculty=faculty)
#         groups = ClassGroup.objects.filter(department__faculty=faculty)
#         secretary_notes = SecretaryNote.objects.filter(faculty=faculty)
#         departments = Department.objects.filter(faculty=faculty)

#         avg_progress = (
#             teaching_progress.aggregate(Avg("progress_percentage"))[
#                 "progress_percentage__avg"
#             ]
#             or 0
#         )

#         return {
#             "total_timetables": timetables.count(),
#             "published_timetables": timetables.filter(status="published").count(),
#             "teaching_progress_avg": round(avg_progress, 2),
#             "total_teachers": workloads.values("teacher").distinct().count(),
#             "total_students": groups.aggregate(
#                 Count("students", distinct=True)
#             )["students__count"]
#             or 0,
#             "total_departments": departments.count(),
#             "total_class_groups": groups.count(),
#             "pending_secretary_notes": secretary_notes.filter(
#                 is_resolved=False
#             ).count(),
#         }
