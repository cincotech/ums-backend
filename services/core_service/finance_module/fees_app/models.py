from django.db import models


class FeesSheet(models.Model):
    class_fk = models.ForeignKey('class_app.Class', on_delete=models.CASCADE)
    academic_year = models.ForeignKey('university_app.AcademicYear', on_delete=models.CASCADE)
    base_amount = models.DecimalField(max_digits=10, decimal_places=2)
    installements = models.JSONField(default=list, blank=True)

    class Meta:
        app_label = 'fees_app'
