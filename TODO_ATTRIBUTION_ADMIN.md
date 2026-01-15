# TODO - Attribution Admin Customization

## Task
Modify the AttributionAdmin to display columns in the requested order:
| Course | Teacher Principal | Statut | Teacher Remplaçant | Statut | Année |

## Steps Completed
- [x] Analyze the current AttributionAdmin structure
- [x] Plan the column reordering

## Steps to Implement
- [x] Update AttributionAdmin.list_display to show:
  1. id
  2. course
  3. principal_teacher_name (Teacher Principal)
  4. status_principal_teacher (Statut)
  5. substitute_teacher_name (Teacher Remplaçant)
  6. status_substitute_teacher (Statut)
  7. academic_year (Année)
  8. date_attribution

## File to Edit
- /home/elvis-brown/django-projects/ums-backend/services/core_service/academic_module/teacher_app/admin.py

## Testing
- [x] Access http://127.0.0.1:8000/admin/teacher_app/attribution/
- [x] Verify the table displays with the correct column order

