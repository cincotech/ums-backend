import logging

# Create your views here.
from rest_framework.views import APIView

from core.response_handler import error_response, success_response

logger = logging.getLogger("core")


class HelloView(APIView):
    def get(self, request):
        logger.debug("Debug info for developers")
        logger.info("User logged in successfully")
        logger.warning("Low disk space")
        logger.error("Payment process failed")
        logger.critical("Database connection lost!")
        try:
            data = {"message": 10 / 0}
            logger.error("An error occurred", exc_info=True)
            return success_response(data=data)
        except Exception as e:
            return error_response(message="Something went wrong", errors=str(e))
