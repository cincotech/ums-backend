from rest_framework import permissions


# -----------------------------
# Single Role Permissions
# -----------------------------
class RolePermission(permissions.BasePermission):
    """
    Generic role-based permission.
    """

    allowed_roles = []

    def has_permission(self, request, view):
        return (
            request.user.is_authenticated
            and request.user.role.name in self.allowed_roles
        )


# -----------------------------
# Define Permissions Per Role
# -----------------------------
class IsSuperAdmin(RolePermission):
    allowed_roles = ["super_admin"]


class IsRector(RolePermission):
    allowed_roles = ["rector"]

class IsSuperAdminCreateOnly(IsSuperAdmin):
    def has_permission(self, request, view):
        if request.method == "POST":
            return super().has_permission(request, view)
        return True


class IsDirectorAcademic(RolePermission):
    allowed_roles = ["director_academic"]


class IsDirectorQuality(RolePermission):
    allowed_roles = ["director_quality_assurance"]


class IsDean(RolePermission):
    allowed_roles = ["dean"]


class IsStudentService(RolePermission):
    allowed_roles = ["student_service"]


class IsFinanceService(RolePermission):
    allowed_roles = ["finance_service"]


class IsGeneralService(RolePermission):
    allowed_roles = ["general_service"]


class IsRectorOffice(RolePermission):
    allowed_roles = ["rector_office"]


class IsAcademicAffairs(RolePermission):
    allowed_roles = ["academic_affairs"]


class IsTeacher(RolePermission):
    allowed_roles = ["teacher"]


class IsSupervisor(RolePermission):
    allowed_roles = ["supervisor"]


class IsStudent(RolePermission):
    allowed_roles = ["student"]


class IsDelegate(RolePermission):
    allowed_roles = ["delegate"]


class IsAlumni(RolePermission):
    allowed_roles = ["alumni"]


# -----------------------------
# Combined Role Permissions
# -----------------------------
class IsSuperAdminOrRector(RolePermission):
    allowed_roles = ["super_admin", "rector"]


class IsTeacherOrdelegate(RolePermission):
    allowed_roles = ["teacher", "delegate"]


class IsStaff(RolePermission):
    allowed_roles = [
        "super_admin",
        "rector",
        "director_academic",
        "director_quality_assurance",
        "dean",
        "student_service",
        "finance_service",
        "general_service",
        "rector_office",
        "academic_affairs",
        "teacher",
        "supervisor",
    ]
