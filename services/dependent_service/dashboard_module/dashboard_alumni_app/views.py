# from rest_framework import status, viewsets
# from rest_framework.decorators import action
# from rest_framework.response import Response

# from services.dependent_service.dashboard_module.dashboard_student_services_app.models import (
#     DocumentRequest,
# )

# from .models import (
#     AlumniDonation,
#     AlumniEvent,
#     AlumniProfile,
#     AlumniTestimonial,
#     JobOffer,
#     MentorshipProgram,
# )
# from .serializers import (
#     AlumniDonationSerializer,
#     AlumniEventRegistrationSerializer,
#     AlumniEventSerializer,
#     AlumniProfileSerializer,
#     AlumniTestimonialSerializer,
#     DocumentRequestSerializer,
#     JobOfferSerializer,
#     MentorshipProgramSerializer,
# )
# from .services import AlumniService


# class AlumniProfileViewSet(viewsets.ModelViewSet):
#     queryset = AlumniProfile.objects.all()
#     serializer_class = AlumniProfileSerializer

#     @action(detail=False, methods=["get"])
#     def search(self, request):
#         sector = request.query_params.get("sector")
#         city = request.query_params.get("city")
#         company = request.query_params.get("company")
#         alumni = AlumniService.search_alumni(sector, city, company)
#         serializer = self.get_serializer(alumni, many=True)
#         return Response(serializer.data)


# class JobOfferViewSet(viewsets.ModelViewSet):
#     queryset = JobOffer.objects.filter(is_active=True)
#     serializer_class = JobOfferSerializer


# class MentorshipProgramViewSet(viewsets.ModelViewSet):
#     queryset = MentorshipProgram.objects.all()
#     serializer_class = MentorshipProgramSerializer


# class AlumniTestimonialViewSet(viewsets.ModelViewSet):
#     queryset = AlumniTestimonial.objects.filter(is_published=True)
#     serializer_class = AlumniTestimonialSerializer


# class AlumniEventViewSet(viewsets.ModelViewSet):
#     queryset = AlumniEvent.objects.all()
#     serializer_class = AlumniEventSerializer

#     @action(detail=True, methods=["post"])
#     def register(self, request, pk=None):
#         alumni_id = request.data.get("alumni_id")
#         try:
#             registration = AlumniService.register_for_event(alumni_id, pk)
#             serializer = AlumniEventRegistrationSerializer(registration)
#             return Response(serializer.data, status=status.HTTP_201_CREATED)
#         except Exception as e:
#             return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)


# class AlumniDonationViewSet(viewsets.ModelViewSet):
#     queryset = AlumniDonation.objects.all()
#     serializer_class = AlumniDonationSerializer


# class DocumentRequestViewSet(viewsets.ModelViewSet):
#     queryset = DocumentRequest.objects.all()
#     serializer_class = DocumentRequestSerializer
