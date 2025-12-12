from rest_framework import mixins, viewsets


class UniversityFilterMixin:
    """Mixin to automatically filter by user's university"""

    def get_queryset(self):
        """Filter queryset by user's university"""
        if hasattr(self.request, "user") and self.request.user.is_authenticated:
            try:
                return self.queryset.filter(university=self.request.user.university)
            except AttributeError:
                pass
        return self.queryset.none()

    def perform_create(self, serializer):
        """Automatically set university on creation"""
        if hasattr(self.request, "user") and self.request.user.is_authenticated:
            serializer.save(
                university=self.request.user.university, created_by=self.request.user
            )
        else:
            serializer.save()

    def perform_update(self, serializer):
        """Automatically set modified_by on update"""
        if hasattr(self.request, "user") and self.request.user.is_authenticated:
            serializer.save(modified_by=self.request.user)
        else:
            serializer.save()


class UniversityCreateModelMixin:
    """Mixin for university-specific create operations"""

    def create(self, request, *args, **kwargs):
        """Create with university context"""
        try:
            if hasattr(request.user, "university"):
                university = request.user.university
            else:
                from rest_framework import status
                from rest_framework.response import Response

                return Response(
                    {"error": "University not found for current user"},
                    status=status.HTTP_403_FORBIDDEN,
                )

            serializer = self.get_serializer(data=request.data)
            serializer.is_valid(raise_exception=True)

            # Add university context
            if hasattr(serializer.instance, "university"):
                serializer.instance.university = university

            self.perform_create(serializer)
            headers = self.get_success_headers(serializer.data)
            return Response(
                serializer.data, status=status.HTTP_201_CREATED, headers=headers
            )

        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)


class UniversityRetrieveUpdateDestroyModelMixin:
    """Mixin for university-specific retrieve, update, destroy operations"""

    def get_object(self):
        """Get object filtered by university"""
        obj = super().get_object()

        # Verify university access
        if hasattr(obj, "university") and hasattr(self.request.user, "university"):
            if obj.university != self.request.user.university:
                from rest_framework.exceptions import PermissionDenied

                raise PermissionDenied("Access denied to this university's data")

        return obj


class UniversityModelViewSet(
    UniversityFilterMixin,
    UniversityCreateModelMixin,
    UniversityRetrieveUpdateDestroyModelMixin,
    mixins.ListModelMixin,
    mixins.CreateModelMixin,
    mixins.RetrieveModelMixin,
    mixins.UpdateModelMixin,
    mixins.DestroyModelMixin,
    viewsets.GenericViewSet,
):
    """Base ViewSet for university-administered models"""

    pass
