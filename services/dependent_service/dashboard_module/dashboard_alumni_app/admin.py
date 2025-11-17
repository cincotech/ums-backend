from django.contrib import admin

from .models import (
    AlumniDonation,
    AlumniEvent,
    AlumniEventRegistration,
    AlumniProfile,
    AlumniTestimonial,
    JobOffer,
    MentorshipProgram,
)

admin.site.register(AlumniProfile)
admin.site.register(JobOffer)
admin.site.register(MentorshipProgram)
admin.site.register(AlumniTestimonial)
admin.site.register(AlumniEvent)
admin.site.register(AlumniEventRegistration)
admin.site.register(AlumniDonation)
