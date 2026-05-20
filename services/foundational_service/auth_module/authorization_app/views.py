# Create your views here.
from django.db import IntegrityError
from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAdminUser, IsAuthenticated
from rest_framework.response import Response

from core.views import BaseViewSet
from services.foundational_service.auth_module.authentication_app.serializers import (
    RoleSerializer,
)
from services.foundational_service.auth_module.user_app.models import Role

from .models import Profile, Supervisor
from .serializers import ProfileSerializer, SupervisorSerializer


class ProfileViewSet(BaseViewSet):
    serializer_class = ProfileSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        role_name = getattr(user.role, "name", "").lower() if getattr(user, "role", None) else ""

        # STAFF / SUPERUSER / admin role → voir tous les profils
        if user.is_staff or user.is_superuser or role_name in {"admin", "super_admin"}:
            return Profile.objects.select_related("user")

        # NORMAL USER → only his profile
        return Profile.objects.filter(user=user)

    def perform_create(self, serializer):
        user = self.request.user

        role_name = (
            getattr(user.role, "name", "").lower()
            if getattr(user, "role", None)
            else ""
        )

        is_admin = (
            user.is_staff
            or user.is_superuser
            or role_name in {"admin", "super_admin"}
        )

        if not is_admin:
            serializer.save(user=user)
        else:
            serializer.save()


class SupervisorViewSet(BaseViewSet):
    queryset = Supervisor.objects.select_related("user")
    serializer_class = SupervisorSerializer
    permission_classes = [IsAuthenticated]

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class AvailableRoleView(viewsets.ReadOnlyModelViewSet):
    """
    List all roles available in the system
    """

    queryset = Role.objects.all()
    serializer_class = RoleSerializer
    permission_classes = [IsAuthenticated]


class RoleViewSet(viewsets.ModelViewSet):
    """
    Admin can create/update/delete roles and reassign users
    """

    queryset = Role.objects.all()
    serializer_class = RoleSerializer
    permission_classes = [IsAdminUser]

    def destroy(self, request, *args, **kwargs):
        try:
            role = self.get_object()
            role.delete()
            return Response(
                {"message": f"Role '{role.name}' deleted successfully."}, status=200
            )
        except Role.DoesNotExist:
            return Response({"error": "Role not found."}, status=404)
        except IntegrityError:
            user_count = role.users.count()
            return Response(
                {
                    "error": f"Cannot delete role '{role.name}' because it has {user_count} user(s)."
                },
                status=400,
            )

    @action(detail=True, methods=["post"], url_path="reassign")
    def reassign(self, request, pk=None):
        old_role = self.get_object()
        new_role_id = request.data.get("new_role_id")
        new_role = Role.objects.get(id=new_role_id) if new_role_id else None
        users = old_role.users.all()
        users.update(role=new_role)
        return Response(
            {
                "message": f"Reassigned {users.count()} users from role '{old_role.name}' to '{new_role.name if new_role else 'None'}'."
            },
            status=200,
        )
