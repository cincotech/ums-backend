from django.core.management.base import BaseCommand

from ...models import ScheduleSlot


class Command(BaseCommand):
    help = "Create multiple academic schedule slots per day (including Sunday)"

    def handle(self, *args, **kwargs):
        ScheduleSlot.objects.all().delete()
        self.stdout.write(self.style.WARNING("Cleared existing schedule slots..."))

        # Academic activity per day
        day_activity = {
            "Monday": "Academic Opening & Core Courses",
            "Tuesday": "Technical & Practical Courses",
            "Wednesday": "Midweek Academic Session",
            "Thursday": "Advanced & Systems Courses",
            "Friday": "Assessments & Tutorials",
            "Saturday": "Labs, Revision & Special Programs",
            "Sunday": "Examinations & Make-up Classes",
        }

        # Standard time slots
        time_slots = [
            ("08:00:00", "10:00:00"),
            ("10:15:00", "12:15:00"),
            ("13:00:00", "15:00:00"),
            ("15:15:00", "17:30:00"),
        ]

        created = 0

        for day, activity in day_activity.items():
            for index, (start, end) in enumerate(time_slots, start=1):
                ScheduleSlot.objects.create(
                    day_of_week=day,
                    start_time=start,
                    end_time=end,
                    schedule_name=f"{activity} (Slot {index})",
                )
                created += 1

                self.stdout.write(
                    self.style.SUCCESS(
                        f"✓ {day} | {start}-{end} | {activity} (Slot {index})"
                    )
                )

        self.stdout.write(
            self.style.SUCCESS(
                f"\n✅ {created} academic schedule slots created successfully"
            )
        )
