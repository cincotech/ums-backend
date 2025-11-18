# Admin registrations removed - models have been consolidated
# These models are now registered in dashboard_shared_app/admin.py
#
# If you need to customize the admin for super admin dashboard specifically,
# you can import and re-register with custom admin classes:
#
# from django.contrib import admin
# from services.dependent_service.dashboard_module.dashboard_shared_app.models import (
#     AuditLog,
#     BackupRecord,
#     SystemConfiguration,
# )
#
# Then create custom admin classes as needed
