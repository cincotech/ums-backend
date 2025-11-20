import base64
import json

from django.core.exceptions import ObjectDoesNotExist

from .models import StudentCard


def decode_qr_to_student_card(encoded_data):
    """
    Decode base64-encoded QR data and return the corresponding StudentCard instance.

    Args:
        encoded_data (str): Base64-encoded JSON string from QR.

    Returns:
        StudentCard instance or None if not found/invalid data.
    """
    try:
        # Decode from Base64
        decoded_bytes = base64.b64decode(encoded_data)
        json_str = decoded_bytes.decode("utf-8")
        data = json.loads(json_str)

        # Retrieve the StudentCard instance by card_number or student_id
        card_number = data.get("card_number")
        student_id = data.get("student_id")

        if card_number:
            # Try to get by card number first
            return StudentCard.objects.get(card_number=card_number)
        elif student_id:
            # Fallback: get latest card of student
            return StudentCard.objects.filter(student__id=student_id).latest(
                "issue_date"
            )
        else:
            return None

    except (
        ValueError,
        json.JSONDecodeError,
        base64.binascii.Error,
        ObjectDoesNotExist,
    ):
        # Handle errors and return None
        return None
