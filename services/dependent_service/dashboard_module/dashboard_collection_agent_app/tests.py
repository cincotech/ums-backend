# from django.contrib.auth import get_user_model
# from django.test import TestCase
# from rest_framework import status
# from rest_framework.test import APIClient

# from .models import Bank, Wording

# User = get_user_model()


# class BankAPITestCase(TestCase):
#     def setUp(self):
#         self.client = APIClient()
#         self.user = User.objects.create_user(email="test@test.com", password="test123")
#         self.client.force_authenticate(user=self.user)
#         self.bank = Bank.objects.create(bank_name="BCB", bank_abreviation="BCB")

#     def test_list_banks(self):
#         response = self.client.get("/dashboard/finance/banks/")
#         self.assertEqual(response.status_code, status.HTTP_200_OK)

#     def test_create_bank(self):
#         data = {"bank_name": "Ecobank", "bank_abreviation": "ECO"}
#         response = self.client.post("/dashboard/finance/banks/", data)
#         self.assertEqual(response.status_code, status.HTTP_201_CREATED)


# class WordingAPITestCase(TestCase):
#     def setUp(self):
#         self.client = APIClient()
#         self.user = User.objects.create_user(email="test@test.com", password="test123")
#         self.client.force_authenticate(user=self.user)

#     def test_list_wordings(self):
#         Wording.objects.create(wording_name="Frais inscription")
#         response = self.client.get("/dashboard/finance/wordings/")
#         self.assertEqual(response.status_code, status.HTTP_200_OK)


# class PaymentAPITestCase(TestCase):
#     def setUp(self):
#         self.client = APIClient()
#         self.user = User.objects.create_user(email="test@test.com", password="test123")
#         self.client.force_authenticate(user=self.user)

#     def test_filter_payment_by_status(self):
#         response = self.client.get(
#             "/dashboard/finance/payments/?payment_status=unverified"
#         )
#         self.assertEqual(response.status_code, status.HTTP_200_OK)

#     def test_filter_payment_by_method(self):
#         response = self.client.get(
#             "/dashboard/finance/payments/?payment_method=mobile_money"
#         )
#         self.assertEqual(response.status_code, status.HTTP_200_OK)
