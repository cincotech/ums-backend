# from services.dependent_service.dashboard_module.dashboard_student_services_app.models import (
#     DocumentRequest,
# )

# from .models import (
#     AlumniDonation,
#     AlumniEventRegistration,
#     AlumniProfile,
#     AlumniTestimonial,
#     JobOffer,
# )


# class AlumniService:
#     @staticmethod
#     def update_profile(alumni_id, profile_data):
#         return AlumniProfile.objects.filter(id=alumni_id).update(**profile_data)

#     @staticmethod
#     def search_alumni(sector=None, city=None, company=None):
#         queryset = AlumniProfile.objects.all()
#         if sector:
#             queryset = queryset.filter(sector=sector)
#         if city:
#             queryset = queryset.filter(city__icontains=city)
#         if company:
#             queryset = queryset.filter(company__icontains=company)
#         return queryset

#     @staticmethod
#     def create_job_offer(alumni_id, job_data):
#         alumni = AlumniProfile.objects.get(id=alumni_id)
#         return JobOffer.objects.create(alumni=alumni, **job_data)

#     @staticmethod
#     def register_as_mentor(alumni_id, expertise_area):
#         alumni = AlumniProfile.objects.get(id=alumni_id)
#         alumni.is_mentor = True
#         alumni.save()
#         return alumni

#     @staticmethod
#     def create_testimonial(alumni_id, testimonial_data):
#         alumni = AlumniProfile.objects.get(id=alumni_id)
#         return AlumniTestimonial.objects.create(alumni=alumni, **testimonial_data)

#     @staticmethod
#     def register_for_event(alumni_id, event_id):
#         return AlumniEventRegistration.objects.create(
#             alumni_id=alumni_id, event_id=event_id
#         )

#     @staticmethod
#     def make_donation(alumni_id, donation_data):
#         alumni = AlumniProfile.objects.get(id=alumni_id)
#         return AlumniDonation.objects.create(alumni=alumni, **donation_data)

#     @staticmethod
#     def request_document(alumni_id, document_data):
#         alumni = AlumniProfile.objects.get(id=alumni_id)
#         return DocumentRequest.objects.create(student=alumni.student, **document_data)
