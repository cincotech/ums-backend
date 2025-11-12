import base64
import json
import logging
import os
import random
import string
from io import BytesIO

import segno
from django.conf import settings
from django.core.files.storage import default_storage
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.utils import timezone
from PIL import Image

logger = logging.getLogger(__name__)


def send_register_otp(device):
    """
    Send a universal email for University Management System using EmailDevice.
    This function automatically fetches the user, token, and expiry from the device.
    """
    user = device.user
    email = user.email
    first_name = getattr(user, "first_name", "")
    last_name = getattr(user, "last_name", "")

    otp = getattr(device, "token", None)
    otp_expiry = getattr(device, "valid_until", None)

    # Make sure the OTP expiry is timezone-aware string
    if otp_expiry:
        otp_expiry = otp_expiry.astimezone(timezone.get_current_timezone()).strftime(
            "%Y-%m-%d %H:%M:%S %Z"
        )

    # Login URL (change to your front-end login page)
    login_url = "https://your-ums-domain.com/login"

    # Support email
    support_email = "support@ums.com"

    # Current year for footer
    current_year = timezone.now().year

    # Render HTML content using Tailwind template
    html_content = render_to_string(
        "emails/ums_send_register_otp.html",
        {
            "first_name": first_name,
            "last_name": last_name,
            "email": email,
            "otp": otp,
            "otp_expiry": otp_expiry,
            "login_url": login_url,
            "support_email": support_email,
            "current_year": current_year,
        },
    )

    subject = "Your University Management System Account"
    from_email = support_email
    to_email = [email]

    email_message = EmailMultiAlternatives(
        subject=subject, body=html_content, from_email=from_email, to=to_email
    )
    email_message.attach_alternative(html_content, "text/html")
    email_message.send()

    return True


def send_otp_email(device, purpose="authentication", valid_minutes=10):
    """
    Send OTP email using the EmailDevice.
    """
    user = device.user
    otp = getattr(device, "token", None)
    otp_expiry = getattr(device, "valid_until", None)

    # Make sure the OTP expiry is timezone-aware string
    if otp_expiry:
        otp_expiry = otp_expiry.astimezone(timezone.get_current_timezone()).strftime(
            "%Y-%m-%d %H:%M:%S %Z"
        )

    device.save()

    context = {
        "user": user,
        "otp": otp,
        "purpose": purpose.capitalize(),  # e.g., "Login", "Password Reset"
        "valid_minutes": otp_expiry,
        "year": timezone.now().year,
        "site_url": "https://ums.example.com",
    }

    subject = f"Your OTP for {purpose.capitalize()}"
    html_content = render_to_string("emails/ums_send_otp.html", context)
    from_email = "no-reply@ums.example.com"
    to_email = user.email

    msg = EmailMultiAlternatives(subject, html_content, from_email, [to_email])
    msg.attach_alternative(html_content, "text/html")
    msg.send()


def generate_qr_code_base64(
    data, scale=10, border=4, dark="#000000", light="#FFFFFF", include_logo=False
):
    """
    Generate a QR code (base64 only, not saved to disk).
    Optionally embed a logo from media/logo/logo.png.

    Args:
        data (str): Data to encode in QR code.
        scale (int): Scale of the QR code.
        border (int): Border around the QR.
        dark (str): Dark color.
        light (str): Light color.
        include_logo (bool): Whether to embed logo.

    Returns:
        str: Base64 string of QR code image (data:image/png;base64,...)
    """
    try:
        qr = segno.make(data, error="L")

        buffer = BytesIO()
        qr.save(buffer, kind="png", scale=scale, border=border, dark=dark, light=light)
        buffer.seek(0)
        qr_image = Image.open(buffer)

        if include_logo:
            logo_path = os.path.join(settings.BASE_DIR, "media", "logo", "logo.png")
            if os.path.exists(logo_path):
                logo = Image.open(logo_path)
                qr_size = qr_image.size[0]
                logo_size = qr_size // 4
                logo = logo.resize((logo_size, logo_size), Image.Resampling.LANCZOS)
                logo_position = ((qr_size - logo_size) // 2, (qr_size - logo_size) // 2)
                qr_image.paste(
                    logo, logo_position, logo if logo.mode == "RGBA" else None
                )
            else:
                logger.warning(f"Logo not found at {logo_path}")

        output_buffer = BytesIO()
        qr_image.save(output_buffer, format="PNG")
        img_base64 = base64.b64encode(output_buffer.getvalue()).decode("utf-8")

        return f"data:image/png;base64,{img_base64}"

    except Exception as e:
        logger.error(f"Failed to generate base64 QR code: {e}")
        raise


def generate_qr_code(
    data, file_name, scale=10, border=4, dark="#000000", light="#FFFFFF"
):
    """
    Generates a customizable QR code with an embedded logo, removes existing file if present,
    saves it to the qrcodes folder, and returns base64 and URL.
    Args:
        data (str): The data to encode in the QR code (e.g., URL).
        file_name (str): The filename for the QR code (e.g., 'totp_123.png'), saved in qrcodes folder.
        scale (int): Scaling factor for QR code size (default: 10).
        border (int): Border size around the QR code (default: 4).
        dark (str): Hex color for the QR code pattern (default: black).
        light (str): Hex color for the background (default: white).
    Returns:
        dict: A dictionary containing the base64-encoded image and the image URL.
    """
    try:
        # Construct the file path in qrcodes folder
        relative_file_path = os.path.join("qrcodes", file_name)
        full_file_path = os.path.join(settings.MEDIA_ROOT, relative_file_path)

        # Remove the file if it already exists
        if default_storage.exists(full_file_path):
            logger.info(f"Removing existing QR code file: {full_file_path}")
            default_storage.delete(full_file_path)

        # Initialize QR code with segno
        qr = segno.make(
            data, error="L"
        )  # Error correction level: L (low, ~7% recovery)

        # Generate QR code image
        buffer = BytesIO()
        qr.save(
            buffer,
            kind="png",
            scale=scale,
            border=border,
            dark=dark,  # Custom dark color
            light=light,  # Custom background color
        )

        # Embed the logo using BASE_DIR
        logo_path = os.path.join(settings.BASE_DIR, "media", "logo", "logo.png")
        if os.path.exists(logo_path):
            qr_image = Image.open(buffer)
            logo = Image.open(logo_path)

            # Resize logo to fit within QR code (e.g., 25% of QR code size)
            qr_size = qr_image.size[0]
            logo_size = qr_size // 4
            logo = logo.resize((logo_size, logo_size), Image.Resampling.LANCZOS)

            # Calculate logo position (center)
            logo_position = ((qr_size - logo_size) // 2, (qr_size - logo_size) // 2)

            # Paste logo onto QR code
            qr_image.paste(logo, logo_position, logo if logo.mode == "RGBA" else None)
            buffer = BytesIO()
            qr_image.save(buffer, format="PNG")
        else:
            logger.warning(f"Logo file not found at: {logo_path}")

        # Generate base64 string
        img_data = buffer.getvalue()
        img_base64 = base64.b64encode(img_data).decode("utf-8")

        # Ensure the qrcodes directory exists
        os.makedirs(os.path.dirname(full_file_path), exist_ok=True)

        # Save the image to disk
        with default_storage.open(full_file_path, "wb") as f:
            f.write(img_data)

        logger.info(f"QR code generated and saved: {full_file_path}")

        # Construct the media URL for the file
        media_url = getattr(settings, "MEDIA_URL", "/media/")
        qr_code_url = os.path.join(media_url, relative_file_path).replace("\\", "/")

        return {
            "base64_image": f"data:image/png;base64,{img_base64}",
            "qr_code_url": qr_code_url,
        }

    except Exception as e:
        logger.error(f"Failed to process QR code for data: {data}. Error: {str(e)}")
        raise


def validate_json_field(data, field_name):
    """
    Validates and sanitizes a JSON field to ensure it is a list.
    Args:
        data: The data to validate (expected to be a list).
        field_name (str): The name of the field for logging purposes.
    Returns:
        list: The validated and sanitized list.
    Raises:
        ValueError: If the data is not a valid list.
    """
    if not isinstance(data, list):
        logger.error(f"JSON validation failed for {field_name}: Data is not a list")
        raise ValueError(f"{field_name} must be a list")
    sanitized_data = [item for item in data if item]
    logger.info(f"Validated JSON field {field_name}: {sanitized_data}")
    return sanitized_data


def export_to_json(data):
    """
    Exports the provided data to a JSON string.
    Args:
        data: The data to export (e.g., dict, list).
    Returns:
        str: The JSON string representation of the data.
    """
    try:
        json_data = json.dumps(data, indent=2, ensure_ascii=False)
        logger.info("Data exported to JSON successfully")
        return json_data
    except (TypeError, ValueError) as e:
        logger.error(f"JSON export failed: {str(e)}")
        raise ValueError(f"Failed to export data to JSON: {str(e)}")


def generate_custom_token():
    """Generate a custom token in the format '17fa3-81788'"""
    characters = string.ascii_lowercase + string.digits
    part1 = "".join(random.choice(characters) for _ in range(5))
    part2 = "".join(random.choice(characters) for _ in range(5))
    return f"{part1}-{part2}"


def get_serializer_error_message(errors):
    """
    Extrait un message d'erreur principal à partir des erreurs de validation du serializer.
    Retourne un message clair et précis basé sur le premier champ en erreur.
    """
    if not errors:
        return "Validation failed"

    # Si errors est un dictionnaire (cas typique pour serializer.errors)
    if isinstance(errors, dict):
        # Prendre le premier champ en erreur
        for field, error_list in errors.items():
            # Les erreurs sont souvent une liste de messages
            if isinstance(error_list, list) and error_list:
                # Capitaliser le nom du champ et ajouter le message d'erreur
                error_message = error_list[0]
                return f"{field.capitalize()} {error_message.lower()}"
            else:
                return f"{field.capitalize()} validation failed: {str(error_list)}"
    # Si errors est une liste ou un autre type, retourner une version stringifiée
    return str(errors)
