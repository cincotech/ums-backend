#!/usr/bin/env python3
"""
Script to fix all import issues in dashboard module after consolidation
"""

import os


def fix_file_imports(file_path, old_imports, new_imports):
    """Fix imports in a single file"""
    try:
        with open(file_path, "r") as f:
            content = f.read()

        # Replace old imports with new ones
        for old_import, new_import in zip(old_imports, new_imports):
            content = content.replace(old_import, new_import)

        with open(file_path, "w") as f:
            f.write(content)

        print(f"Fixed imports in {file_path}")
        return True
    except Exception as e:
        print(f"Error fixing {file_path}: {e}")
        return False


def main():
    """Main function to fix all import issues"""

    # Dashboard module base path
    base_path = "/home/ndikumana/Documents/Python/Django/ums/services/dependent_service/dashboard_module"

    # Files to fix with their import mappings
    fixes = [
        # Collection Agent App
        {
            "files": [
                f"{base_path}/dashboard_collection_agent_app/serializers.py",
                f"{base_path}/dashboard_collection_agent_app/views.py",
                f"{base_path}/dashboard_collection_agent_app/services.py",
                f"{base_path}/dashboard_collection_agent_app/admin.py",
            ],
            "old_imports": [
                "from .models import (\n    PaymentInstallment,",
                "PaymentInstallment,",
                "PaymentInstallment.objects",
            ],
            "new_imports": [
                "from services.core_service.finance_module.payment_app.models import Payment\nfrom .models import (",
                "",
                "Payment.objects",
            ],
        },
        # Academic Secretary App
        {
            "files": [
                f"{base_path}/dashboard_academic_secretary_app/views.py",
                f"{base_path}/dashboard_academic_secretary_app/services.py",
                f"{base_path}/dashboard_academic_secretary_app/admin.py",
            ],
            "old_imports": [
                "from .models import (\n    ExamSession, ExamAttendance,",
                "ExamSession,",
                "ExamAttendance,",
            ],
            "new_imports": [
                "from services.dependent_service.exam_module.exam_app.models import Exam\nfrom services.dependent_service.exam_module.attendance_app.models import ExamAttendance\nfrom .models import (",
                "",
                "",
            ],
        },
        # Alumni App
        {
            "files": [
                f"{base_path}/dashboard_alumni_app/views.py",
                f"{base_path}/dashboard_alumni_app/services.py",
            ],
            "old_imports": ["AlumniDocumentRequest.objects", "AlumniDocumentRequest"],
            "new_imports": ["DocumentRequest.objects", "DocumentRequest"],
        },
    ]

    # Apply fixes
    for fix_group in fixes:
        for file_path in fix_group["files"]:
            if os.path.exists(file_path):
                fix_file_imports(
                    file_path, fix_group["old_imports"], fix_group["new_imports"]
                )

    print("All import fixes completed!")


if __name__ == "__main__":
    main()
