import json

from django.http import JsonResponse
from rest_framework.permissions import SAFE_METHODS

from services.core_service.academic_module.university_app.models import AcademicYear


class AcademicYearLockMiddleware:

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):

        print("\n========== MIDDLEWARE ==========")
        print("METHOD:", request.method)
        print("PATH:", request.path)

        if request.method in SAFE_METHODS:
            print("SAFE METHOD -> SKIPPED")
            return self.get_response(request)

        # Query params
        print("GET PARAMS:", request.GET.dict())

        academic_year_id = request.GET.get(
            "academic_year_id"
        )

        # Debug raw body
        print("RAW BODY:", request.body)

        # Handle JSON body
        if not academic_year_id and request.body:
            try:
                body = json.loads(request.body)

                print("PARSED BODY:", body)

                academic_year_id = body.get(
                    "academic_year_id"
                )

            except Exception as e:
                print("JSON ERROR:", str(e))

        print("ACADEMIC_YEAR_ID:", academic_year_id)

        if not academic_year_id:
            print("NO ACADEMIC YEAR FOUND")
            return self.get_response(request)

        academic_year = AcademicYear.objects.filter(
            id=academic_year_id
        ).first()

        print("ACADEMIC_YEAR:", academic_year)

        if academic_year:
            print("IS CLOSED:", academic_year.is_closed)

        if academic_year and academic_year.is_closed:
            print("BLOCKED REQUEST")

            return JsonResponse(
                {
                    "detail": (
                        "Cette année académique est fermée."
                    )
                },
                status=403,
            )

        print("REQUEST ALLOWED")

        return self.get_response(request)