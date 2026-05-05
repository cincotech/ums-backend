from django.core.management.base import BaseCommand

from services.core_service.academic_module.class_app.models import Class

# Roman numerals mapping (up to 10)
ROMAN_TO_INT = {
    "I": 1,
    "II": 2,
    "III": 3,
    "IV": 4,
    "V": 5,
    "VI": 6,
    "VII": 7,
    "VIII": 8,
    "IX": 9,
    "X": 10,
}


def detect_level_from_name(class_name: str):
    """
    Detects the level from a class name by reading the last word.
    Examples:
        'BAC I'     -> 1
        'BAC II'    -> 2
        'L3 INFO'   -> None (roman not at end)
        'MASTER III'-> 3
        'G1 GC'     -> None
    Returns None if no roman numeral found at the end.
    """
    parts = class_name.strip().split()
    if not parts:
        return None

    last_word = parts[-1].upper()
    return ROMAN_TO_INT.get(last_word)


class Command(BaseCommand):
    help = "Auto-assign level to classes based on roman numerals at end of class_name (I=1, II=2, ...)"

    def add_arguments(self, parser):
        parser.add_argument(
            "--dry-run",
            action="store_true",
            help="Show what would be updated without saving",
        )
        parser.add_argument(
            "--overwrite",
            action="store_true",
            help="Overwrite existing levels (default: skip classes that already have level != 1)",
        )

    def handle(self, *args, **options):
        dry_run = options["dry_run"]
        overwrite = options["overwrite"]

        classes = Class.objects.all().order_by("class_name")
        total = classes.count()

        self.stdout.write(self.style.WARNING(f"\nScanning {total} classes...\n"))

        updated = 0
        skipped = 0
        not_detected = 0

        for cls in classes:
            detected_level = detect_level_from_name(cls.class_name)

            if detected_level is None:
                self.stdout.write(
                    f"  ⚠️  '{cls.class_name}' → no roman numeral detected, kept level={cls.level}"
                )
                not_detected += 1
                continue

            # Skip if already has a non-default level and overwrite not requested
            if cls.level != 1 and not overwrite:
                self.stdout.write(
                    f"  ⏭️  '{cls.class_name}' → already level={cls.level}, skipped (use --overwrite to force)"
                )
                skipped += 1
                continue

            if cls.level == detected_level:
                self.stdout.write(
                    f"  ✅  '{cls.class_name}' → level={detected_level} already correct"
                )
                skipped += 1
                continue

            self.stdout.write(
                self.style.SUCCESS(
                    f"  ✏️  '{cls.class_name}' → level {cls.level} → {detected_level}"
                )
            )

            if not dry_run:
                cls.level = detected_level
                cls.save(update_fields=["level"])

            updated += 1

        self.stdout.write("\n" + "=" * 50)
        if dry_run:
            self.stdout.write(self.style.WARNING("DRY RUN — no changes saved"))
        self.stdout.write(self.style.SUCCESS(f"Updated  : {updated}"))
        self.stdout.write(self.style.WARNING(f"Skipped  : {skipped}"))
        self.stdout.write(f"No match : {not_detected}")
        self.stdout.write(f"Total    : {total}\n")
