from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import (
    BankViewSet,
    BordereauLineViewSet,
    BordereauViewSet,
    CollectionCorrespondenceViewSet,
    FeesSheetViewSet,
    FinanceDashboardAPIView,
    PaymentInstallementViewSet,
    PaymentPlanViewSet,
    PaymentPromiseViewSet,
    PaymentReminderViewSet,
    PaymentViewSet,
    WordingViewSet,
)

router = DefaultRouter()
router.register(r"banks", BankViewSet)
router.register(r"wordings", WordingViewSet)
router.register(r"fees-sheets", FeesSheetViewSet)
router.register(r"payment-installements", PaymentInstallementViewSet)
router.register(r"payment-reminders", PaymentReminderViewSet)
router.register(r"payment-plans", PaymentPlanViewSet)
router.register(r"payment-promises", PaymentPromiseViewSet)
router.register(r"payments", PaymentViewSet)
router.register(r"collection-correspondence", CollectionCorrespondenceViewSet)
router.register(r"bordereaux", BordereauViewSet)
router.register(r"bordereau-lines", BordereauLineViewSet)

urlpatterns = [
    path(
        "overview/",
        FinanceDashboardAPIView.as_view({"get": "overview"}),
        name="finance-overview",
    ),
    path("", include(router.urls)),
]
