from django.test import SimpleTestCase


class GradeWorkflowSmokeTest(SimpleTestCase):
    def test_result_status_choices_are_available(self):
        from services.dependent_service.exam_module.result_app.models import Result

        self.assertIn("draft", [choice[0] for choice in Result.STATUS_CHOICES])
        self.assertIn("submitted", [choice[0] for choice in Result.STATUS_CHOICES])
        self.assertIn("validated", [choice[0] for choice in Result.STATUS_CHOICES])
        self.assertIn("rejected", [choice[0] for choice in Result.STATUS_CHOICES])
