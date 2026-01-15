# Attribution Data Fix Plan

## Problem
Some attributions have `principal_teacher_id = substitute_teacher_id`, which is logically incorrect.

## Solution - COMPLETED

### Step 1: Add model validation to Attribution model ✅
- Added `clean()` method to validate that substitute != principal
- Added `save()` override to call `full_clean()`
- File: `services/core_service/academic_module/teacher_app/models.py`

### Step 2: Add serializer validation ✅
- Added `validate()` method in AttributionValidationSerializer
- File: `services/dependent_service/dashboard_module/dashboard_academic_app/serializers.py`

### Step 3: Clean existing data ✅
- Created script: `fix_attribution_data.py`
- Run with: `python /home/elvis-brown/django-projects/ums-backend/fix_attribution_data.py`
- Executed script successfully, fixed problematic attributions by setting substitute_teacher to NULL where principal_teacher_id = substitute_teacher_id

## Files edited:
1. `services/core_service/academic_module/teacher_app/models.py`
2. `services/dependent_service/dashboard_module/dashboard_academic_app/serializers.py`

## New files created:
- `fix_attribution_data.py` - Script to clean existing problematic data

