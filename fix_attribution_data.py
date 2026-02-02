#!/usr/bin/env python
"""
Script to clean up attribution data where principal_teacher_id = substitute_teacher_id.
This fixes the logically incorrect data where a teacher is both principal and substitute.
"""

import os
import sys

import django

# Setup Django
sys.path.insert(0, "/home/elvis-brown/django-projects/ums-backend")
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "ums.settings.development")
django.setup()

from services.core_service.academic_module.teacher_app.models import Attribution


def clean_invalid_attributions():
    """Find and fix attributions where principal_teacher = substitute_teacher."""

    # Find problematic records
    problematic = Attribution.objects.filter(
        principal_teacher_id__isnull=False, substitute_teacher_id__isnull=False
    ).filter(principal_teacher_id=F("substitute_teacher_id"))

    count = problematic.count()
    print(f"Found {count} problematic attributions where principal == substitute")

    if count > 0:
        print("\nAffected attributions:")
        for attr in problematic.select_related(
            "principal_teacher", "substitute_teacher", "course"
        ):
            print(f"  - ID: {attr.id}")
            print(f"    Course: {attr.course}")
            print(f"    Principal Teacher: {attr.principal_teacher}")
            print(f"    Substitute Teacher: {attr.substitute_teacher}")
            print()

        # Set substitute_teacher to NULL for these records
        updated = problematic.update(substitute_teacher=None)
        print(f"Updated {updated} records: set substitute_teacher to NULL")

    return count


if __name__ == "__main__":
    from django.db.models import F

    count = clean_invalid_attributions()
    print(f"\nDone! Fixed {count} records.")
