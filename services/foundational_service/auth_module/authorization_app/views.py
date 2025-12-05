# Create your views here.
from django.db import IntegrityError
from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAdminUser, IsAuthenticated
from rest_framework.response import Response

from services.foundational_service.auth_module.authentication_app.serializers import (
    RoleSerializer,
)
from services.foundational_service.auth_module.user_app.models import Role


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
