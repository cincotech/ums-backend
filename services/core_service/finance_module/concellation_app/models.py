import uuid

from django.db import models

from services.core_service.finance_module.fees_app.models import FeesSheet
from services.core_service.student_module.inscription_app.models import Inscription


class DebtCancellation(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    inscription = models.ForeignKey(Inscription, on_delete=models.RESTRICT)
    feessheet = models.ForeignKey(
        FeesSheet, on_delete=models.RESTRICT, related_name="payments_debt"
    )
    cancelation_date = models.DateField()
    cancelled_amount = models.PositiveIntegerField()
    reason = models.TextField(null=True, blank=True)

    class Meta:
        db_table = "debt_cancellations"
