from django.db import models


class Payment(models.Model):
    inscription = models.ForeignKey('inscription_app.Inscription', on_delete=models.CASCADE)
    amount_paid = models.DecimalField(max_digits=10, decimal_places=2)
    payment_status = models.CharField(max_length=20, default='pending')

    class Meta:
        app_label = 'payment_app'
