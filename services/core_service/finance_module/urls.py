from django.urls import include, path
from rest_framework.routers import DefaultRouter

from services.core_service.finance_module.concellation_app.views import (
    DebtCancellationViewSet,
)
from services.core_service.finance_module.fees_app.views import (
    FeesSheetViewSet,
    WordingViewSet,
)

router = DefaultRouter()
router.register(r"wordings", WordingViewSet, basename="wording")
router.register(r"fees-sheets", FeesSheetViewSet, basename="fees-sheet")

router.register(
    r"debt-cancellations", DebtCancellationViewSet, basename="debt-cancellation"
)

urlpatterns = [
    path("finance/", include(router.urls)),
]
