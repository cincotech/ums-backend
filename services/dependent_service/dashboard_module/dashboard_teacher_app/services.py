from django.db import transaction
from django.db.models import Avg, Q
from django.utils import timezone

from services.core_service.academic_module.course_app.models import Course
from services.core_service.academic_module.teacher_app.models import Attribution
from services.core_service.student_module.inscription_app.models import Inscription
from services.dependent_service.dashboard_module.dashboard_academic_secretary_app.models import (
    TeacherPaymentClaim,
)
from services.dependent_service.dashboard_module.dashboard_shared_app.models import (
    Message,
    Notification,
)
from services.dependent_service.exam_module.exam_app.models import ExamSupervisor
from services.dependent_service.exam_module.result_app.models import Result
from services.dependent_service.scheduling_module.scheduling_app.models import (
    Attendance,
    Timetable,
)


class TeacherDashboardService:

    @staticmethod
    def get_teacher_dashboard_stats(teacher):
        """Get teacher dashboard overview statistics"""
        current_academic_year = timezone.now().year

        # Count active course attributions
        active_attributions = Attribution.objects.filter(
            Q(principal_teacher=teacher) | Q(substitute_teacher=teacher),
            status_principal_teacher="Accepted",
            academic_year__start_date__year=current_academic_year,
        ).count()

        # Count upcoming exams teacher is supervising
        upcoming_exams = ExamSupervisor.objects.filter(
            supervisor=teacher.user, exam__start_date__gte=timezone.now()
        ).count()

        # Count pending grade entries (courses where not all grades are entered)
        courses = Course.objects.filter(
            attributions__principal_teacher=teacher,
            attributions__status_principal_teacher="Accepted",
        )

        pending_grades = 0
        for course in courses:
            total_students = Inscription.objects.filter(
                class_fk__courses=course, regist_status="Active"
            ).count()

            entered_grades = Result.objects.filter(
                course=course, mark__isnull=False
            ).count()

            if entered_grades < total_students:
                pending_grades += 1

        # Count pending payment claims
        pending_claims = TeacherPaymentClaim.objects.filter(
            teacher=teacher, status__in=["submitted", "verified"]
        ).count()

        # Count unread notifications
        unread_notifications = Notification.objects.filter(
            recipient=teacher.user, is_read=False
        ).count()

        return {
            "active_courses": active_attributions,
            "upcoming_exams": upcoming_exams,
            "pending_grades": pending_grades,
            "pending_claims": pending_claims,
            "unread_notifications": unread_notifications,
        }

    @staticmethod
    def get_teacher_profile(teacher):
        """Get teacher profile information"""
        user = teacher.user

        # Count total courses taught
        total_courses = Attribution.objects.filter(
            Q(principal_teacher=teacher) | Q(substitute_teacher=teacher),
            status_principal_teacher="Accepted",
        ).count()

        # Get recent attributions
        recent_attributions = Attribution.objects.filter(
            Q(principal_teacher=teacher) | Q(substitute_teacher=teacher),
            status_principal_teacher="Accepted",
        ).order_by("-date_attribution")[:5]

        return {
            "teacher_id": teacher.id,
            "full_name": f"{user.first_name} {user.last_name}",
            "email": user.email,
            "phone_number": user.phone_number or "",
            "teacher_grade": teacher.teacher_grade,
            "degree": teacher.degree.name if teacher.degree else "N/A",
            "university": teacher.university.name if teacher.university else "N/A",
            "speciality": teacher.speciality or "N/A",
            "total_courses_taught": total_courses,
            "recent_attributions": recent_attributions,
        }

    @staticmethod
    def get_teacher_attributions(teacher):
        """Get teacher course attributions"""
        attributions = Attribution.objects.filter(
            Q(principal_teacher=teacher) | Q(substitute_teacher=teacher)
        ).select_related(
            "course",
            "academic_year",
            "principal_teacher__user",
            "substitute_teacher__user",
            "submitted_by",
        )

        return attributions

    @staticmethod
    def accept_attribution(attribution_id, teacher):
        """Accept a course attribution"""
        attribution = Attribution.objects.get(id=attribution_id)

        # Check if teacher is principal or substitute
        if attribution.principal_teacher == teacher:
            attribution.status_principal_teacher = "Accepted"
        elif attribution.substitute_teacher == teacher:
            attribution.status_substitute_teacher = "Accepted"
        else:
            raise ValueError("You are not assigned to this attribution")

        attribution.save()

        # Create notification
        Notification.objects.create(
            recipient=teacher.user,
            recipient_type="teacher",
            notification_type="attribution_accepted",
            title="Course Attribution Accepted",
            message=f"You have accepted the attribution for {attribution.course.course_name}",
        )

        return attribution

    @staticmethod
    def refuse_attribution(attribution_id, teacher, comment):
        """Refuse a course attribution"""
        attribution = Attribution.objects.get(id=attribution_id)

        # Check if teacher is principal or substitute
        if attribution.principal_teacher == teacher:
            attribution.status_principal_teacher = "Refused"
        elif attribution.substitute_teacher == teacher:
            attribution.status_substitute_teacher = "Refused"
        else:
            raise ValueError("You are not assigned to this attribution")

        attribution.commentaire = comment
        attribution.save()

        return attribution

    @staticmethod
    def get_teacher_courses(teacher):
        """Get courses currently taught by teacher"""
        current_year = timezone.now().year

        attributions = Attribution.objects.filter(
            Q(principal_teacher=teacher) | Q(substitute_teacher=teacher),
            status_principal_teacher="Accepted",
            academic_year__start_date__year=current_year,
        ).select_related("course", "academic_year")

        courses = []
        for attr in attributions:
            # Get student count for course
            student_count = Inscription.objects.filter(
                class_fk__courses=attr.course, regist_status="Active"
            ).count()

            # Get grade entry progress
            entered_grades = Result.objects.filter(
                course=attr.course, mark__isnull=False
            ).count()

            completion_rate = (
                (entered_grades / student_count * 100) if student_count > 0 else 0
            )

            courses.append(
                {
                    "attribution": attr,
                    "course": attr.course,
                    "student_count": student_count,
                    "grades_entered": entered_grades,
                    "completion_rate": round(completion_rate, 2),
                }
            )

        return courses

    @staticmethod
    def get_course_students(teacher, course_id):
        """Get students enrolled in a course taught by teacher"""
        # Verify teacher teaches this course
        attribution = Attribution.objects.filter(
            Q(principal_teacher=teacher) | Q(substitute_teacher=teacher),
            course_id=course_id,
            status_principal_teacher="Accepted",
        ).first()

        if not attribution:
            raise ValueError("You are not authorized to view this course")

        # Get students from inscriptions
        inscriptions = Inscription.objects.filter(
            class_fk__courses=attribution.course, regist_status="Active"
        ).select_related("student__user", "class_fk")

        students_data = []
        for inscription in inscriptions:
            # Get student's result for this course
            result = Result.objects.filter(
                inscription=inscription, course=attribution.course
            ).first()

            # Get attendance for this student
            attendance_records = Attendance.objects.filter(inscription=inscription)
            total_attendance = attendance_records.count()
            present_count = attendance_records.filter(
                status__in=["present", "justified"]
            ).count()
            attendance_rate = (
                (present_count / total_attendance * 100) if total_attendance > 0 else 0
            )

            students_data.append(
                {
                    "student": inscription.student,
                    "inscription": inscription,
                    "result": result,
                    "attendance_rate": round(attendance_rate, 2),
                }
            )

        return students_data

    @staticmethod
    @transaction.atomic
    def enter_grade(teacher, course_id, inscription_id, session_id, mark):
        """Enter grade for a student"""
        # Verify teacher teaches this course
        attribution = Attribution.objects.filter(
            Q(principal_teacher=teacher) | Q(substitute_teacher=teacher),
            course_id=course_id,
            status_principal_teacher="Accepted",
        ).first()

        if not attribution:
            raise ValueError("You are not authorized to grade this course")

        # Validate mark
        if not 0 <= mark <= 100:
            raise ValueError("Mark must be between 0 and 100")

        # Create or update result
        result, created = Result.objects.update_or_create(
            course_id=course_id,
            inscription_id=inscription_id,
            session_id=session_id,
            defaults={"mark": mark},
        )

        return result

    @staticmethod
    @transaction.atomic
    def bulk_enter_grades(teacher, course_id, session_id, grades_data):
        """Bulk enter grades for multiple students

        grades_data format: [
            {"inscription_id": "uuid", "mark": 75.5},
            {"inscription_id": "uuid", "mark": 80.0},
            ...
        ]
        """
        # Verify teacher teaches this course
        attribution = Attribution.objects.filter(
            Q(principal_teacher=teacher) | Q(substitute_teacher=teacher),
            course_id=course_id,
            status_principal_teacher="Accepted",
        ).first()

        if not attribution:
            raise ValueError("You are not authorized to grade this course")

        results = []
        for grade_data in grades_data:
            mark = grade_data["mark"]

            # Validate mark
            if not 0 <= mark <= 100:
                raise ValueError(f"Mark {mark} must be between 0 and 100")

            result, created = Result.objects.update_or_create(
                course_id=course_id,
                inscription_id=grade_data["inscription_id"],
                session_id=session_id,
                defaults={"mark": mark},
            )
            results.append(result)

        return results

    @staticmethod
    def get_teacher_exams(teacher):
        """Get exams where teacher is supervisor"""
        exam_supervisors = ExamSupervisor.objects.filter(
            supervisor=teacher.user
        ).select_related("exam__course", "exam__exam_type")

        return exam_supervisors

    @staticmethod
    def get_teacher_schedule(teacher):
        """Get teacher teaching schedule"""
        # Get courses taught by teacher
        attributions = Attribution.objects.filter(
            Q(principal_teacher=teacher) | Q(substitute_teacher=teacher),
            status_principal_teacher="Accepted",
        ).select_related("course")

        course_ids = [attr.course.id for attr in attributions]

        # Get timetables for these courses
        timetables = Timetable.objects.filter(
            slots__course_id__in=course_ids
        ).prefetch_related("slots__course", "slots__room", "class_group__class_fk")

        return timetables

    @staticmethod
    @transaction.atomic
    def submit_payment_claim(
        teacher, course_id, hours_taught, hourly_rate, total_amount
    ):
        """Submit payment claim for teaching hours"""
        # Verify teacher teaches this course
        attribution = Attribution.objects.filter(
            Q(principal_teacher=teacher) | Q(substitute_teacher=teacher),
            course_id=course_id,
            status_principal_teacher="Accepted",
        ).first()

        if not attribution:
            raise ValueError("You are not authorized to claim payment for this course")

        # Create payment claim
        claim = TeacherPaymentClaim.objects.create(
            teacher=teacher,
            course_id=course_id,
            hours_taught=hours_taught,
            hourly_rate=hourly_rate,
            total_amount=total_amount,
            status="submitted",
        )

        # Create notification
        Notification.objects.create(
            recipient=teacher.user,
            recipient_type="teacher",
            notification_type="claim_submitted",
            title="Payment Claim Submitted",
            message=f"Your payment claim for {hours_taught} hours has been submitted and is awaiting verification.",
        )

        return claim

    @staticmethod
    def get_teacher_payment_claims(teacher):
        """Get teacher payment claims"""
        claims = TeacherPaymentClaim.objects.filter(teacher=teacher).select_related(
            "course", "verified_by", "approved_by"
        )

        return claims

    @staticmethod
    def get_teacher_notifications(teacher):
        """Get teacher notifications"""
        notifications = Notification.objects.filter(recipient=teacher.user).order_by(
            "-created_at"
        )

        return notifications

    @staticmethod
    def mark_notification_read(notification_id, teacher):
        """Mark notification as read"""
        notification = Notification.objects.get(
            id=notification_id, recipient=teacher.user
        )

        notification.is_read = True
        notification.save()

        return notification

    @staticmethod
    def get_teacher_messages(teacher):
        """Get teacher messages"""
        messages = Message.objects.filter(recipient=teacher.user).order_by("-sent_at")

        return messages

    @staticmethod
    def send_message(teacher, recipient_id, subject, content, message_type):
        """Send message"""
        from services.foundational_service.auth_module.user_app.models import User

        recipient = User.objects.get(id=recipient_id)

        message = Message.objects.create(
            message_type=message_type,
            recipient=recipient,
            sender=teacher.user,
            subject=subject,
            content=content,
        )

        return message

    @staticmethod
    def record_attendance(
        teacher, course_id, inscription_id, attendance_date, status, notes=""
    ):
        """Record student attendance for a class"""
        # Verify teacher teaches this course
        attribution = Attribution.objects.filter(
            Q(principal_teacher=teacher) | Q(substitute_teacher=teacher),
            course_id=course_id,
            status_principal_teacher="Accepted",
        ).first()

        if not attribution:
            raise ValueError(
                "You are not authorized to record attendance for this course"
            )

        # Get or create attendance record
        attendance, created = Attendance.objects.update_or_create(
            inscription_id=inscription_id,
            date=attendance_date,
            defaults={"status": status, "notes": notes},
        )

        return attendance

    @staticmethod
    def get_course_attendance(teacher, course_id):
        """Get attendance records for a course"""
        # Verify teacher teaches this course
        attribution = Attribution.objects.filter(
            Q(principal_teacher=teacher) | Q(substitute_teacher=teacher),
            course_id=course_id,
            status_principal_teacher="Accepted",
        ).first()

        if not attribution:
            raise ValueError(
                "You are not authorized to view attendance for this course"
            )

        # Get inscriptions for this course
        inscriptions = Inscription.objects.filter(
            class_fk__courses=attribution.course, regist_status="Active"
        )

        # Get attendance for these inscriptions
        attendance_records = Attendance.objects.filter(
            inscription__in=inscriptions
        ).select_related("inscription__student__user")

        return attendance_records

    @staticmethod
    def get_teaching_statistics(teacher):
        """Get teaching statistics for teacher"""
        # Get all courses taught
        attributions = Attribution.objects.filter(
            Q(principal_teacher=teacher) | Q(substitute_teacher=teacher),
            status_principal_teacher="Accepted",
        ).select_related("course", "academic_year")

        total_students = 0
        total_grades_entered = 0
        average_grade = 0

        for attr in attributions:
            students = Inscription.objects.filter(
                class_fk__courses=attr.course, regist_status="Active"
            ).count()

            total_students += students

            results = Result.objects.filter(course=attr.course, mark__isnull=False)
            total_grades_entered += results.count()

            avg = results.aggregate(avg=Avg("mark"))["avg"] or 0
            average_grade += avg

        avg_courses = attributions.count()
        average_grade = average_grade / avg_courses if avg_courses > 0 else 0

        return {
            "total_courses": attributions.count(),
            "total_students": total_students,
            "total_grades_entered": total_grades_entered,
            "average_grade": round(average_grade, 2),
        }
