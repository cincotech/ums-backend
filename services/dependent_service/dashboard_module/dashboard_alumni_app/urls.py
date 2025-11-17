from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import (
    AlumniDocumentRequestViewSet,
    AlumniDonationViewSet,
    AlumniEventViewSet,
    AlumniProfileViewSet,
    AlumniTestimonialViewSet,
    JobOfferViewSet,
    MentorshipProgramViewSet,
)

router = DefaultRouter()
router.register(r"profiles", AlumniProfileViewSet)
router.register(r"job-offers", JobOfferViewSet)
router.register(r"mentorship", MentorshipProgramViewSet)
router.register(r"testimonials", AlumniTestimonialViewSet)
router.register(r"events", AlumniEventViewSet)
router.register(r"donations", AlumniDonationViewSet)
router.register(r"document-requests", AlumniDocumentRequestViewSet)

urlpatterns = [
    path("", include(router.urls)),
]
