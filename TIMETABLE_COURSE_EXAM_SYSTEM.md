# Timetable System - Course & Exam Scheduling

## Overview
The timetable system now supports both **course scheduling** (via attribution) and **exam scheduling** (via exam), with clear identification at both timetable and slot levels.

## Model Changes

### 1. ScheduleSlot Model
**New Field: `slot_type`**
- Type: CharField with choices
- Options: `"course"` or `"exam"`
- Default: `"course"`
- Purpose: Identifies if a time slot is for regular courses or exams

**Example:**
```python
# Course slot
course_slot = ScheduleSlot.objects.create(
    day_of_week="Monday",
    start_time="08:00",
    end_time="10:00",
    schedule_name="Morning Session",
    slot_type="course"
)

# Exam slot
exam_slot = ScheduleSlot.objects.create(
    day_of_week="Friday",
    start_time="14:00",
    end_time="16:00",
    schedule_name="Exam Period",
    slot_type="exam"
)
```

### 2. Timetable Model
**New Field: `timetable_type`**
- Type: CharField with choices
- Options: `"course"` or `"exam"`
- Default: `"course"`
- Purpose: Identifies if the entire timetable is for courses or exams

**Existing Fields:**
- `attribution`: ForeignKey to Attribution (for course timetables)
- `exam`: ForeignKey to Exam (for exam timetables)
- `class_groups`: ManyToManyField (multiple groups can share same timetable)

## Usage Scenarios

### Scenario 1: Create Course Timetable
```python
# Create timetable for regular course
timetable = Timetable.objects.create(
    timetable_type="course",
    attribution=attribution,  # Link to course attribution
    exam=None,
    room=room,
    start_date="2024-01-15",
    end_date="2024-05-30",
    status="Planned",
    created_by=dean
)
timetable.class_groups.add(group1, group2)
timetable.slots.add(course_slot1, course_slot2)
```

### Scenario 2: Create Exam Timetable
```python
# Create timetable for exam
exam_timetable = Timetable.objects.create(
    timetable_type="exam",
    attribution=None,
    exam=exam,  # Link to exam
    room=exam_room,
    start_date="2024-06-10",
    end_date="2024-06-10",
    status="Planned",
    created_by=dean
)
exam_timetable.class_groups.add(group1, group2, group3)
exam_timetable.slots.add(exam_slot)
```

### Scenario 3: Mixed Timetable (Both Course & Exam)
```python
# Timetable can have both attribution and exam
mixed_timetable = Timetable.objects.create(
    timetable_type="course",  # Primary type
    attribution=attribution,
    exam=exam,  # Can also reference exam
    room=room,
    start_date="2024-01-15",
    end_date="2024-06-30",
    created_by=dean
)
```

## Filtering & Querying

### Get Course Timetables
```python
course_timetables = Timetable.objects.filter(timetable_type="course")
```

### Get Exam Timetables
```python
exam_timetables = Timetable.objects.filter(timetable_type="exam")
```

### Get Course Slots
```python
course_slots = ScheduleSlot.objects.filter(slot_type="course")
```

### Get Exam Slots
```python
exam_slots = ScheduleSlot.objects.filter(slot_type="exam")
```

### Get Student Schedule (Courses Only)
```python
student_timetables = Timetable.objects.filter(
    class_groups__in=student_class_groups,
    timetable_type="course"
)
```

### Get Student Exams
```python
student_exams = Timetable.objects.filter(
    class_groups__in=student_class_groups,
    timetable_type="exam"
)
```

## Benefits

1. **Clear Identification**: Easy to distinguish between course and exam schedules
2. **Flexible Scheduling**: Can create pure course, pure exam, or mixed timetables
3. **Multiple Groups**: Multiple class groups can share the same timetable
4. **Slot-Level Control**: Each time slot can be identified as course or exam
5. **Dean Control**: Dean can manage both course and exam scheduling through timetables
6. **Student View**: Students see both courses and exams in their schedule

## Migration
Run migration `0007_timetable_exam.py` to apply changes:
- Adds `slot_type` to ScheduleSlot
- Adds `timetable_type` to Timetable
- Adds `exam` ForeignKey to Timetable
