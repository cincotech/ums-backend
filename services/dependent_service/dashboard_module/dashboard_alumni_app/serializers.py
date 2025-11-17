from rest_framework import serializers

from services.dependent_service.dashboard_module.dashboard_student_services_app.models import (
    DocumentRequest,
)

from .models import (
    AlumniDonation,
    AlumniEvent,
    AlumniEventRegistration,
    AlumniProfile,
    AlumniTestimonial,
    JobOffer,
    MentorshipProgram,
)


class AlumniProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = AlumniProfile
        fields = "__all__"


class JobOfferSerializer(serializers.ModelSerializer):
    class Meta:
        model = JobOffer
        fields = "__all__"


class MentorshipProgramSerializer(serializers.ModelSerializer):
    class Meta:
        model = MentorshipProgram
        fields = "__all__"


class AlumniTestimonialSerializer(serializers.ModelSerializer):
    class Meta:
        model = AlumniTestimonial
        fields = "__all__"


class AlumniEventSerializer(serializers.ModelSerializer):
    class Meta:
        model = AlumniEvent
        fields = "__all__"


class AlumniEventRegistrationSerializer(serializers.ModelSerializer):
    class Meta:
        model = AlumniEventRegistration
        fields = "__all__"


class AlumniDonationSerializer(serializers.ModelSerializer):
    class Meta:
        model = AlumniDonation
        fields = "__all__"


class AlumniDocumentRequestSerializer(serializers.ModelSerializer):
    class Meta:
        model = DocumentRequest
        fields = "__all__"
