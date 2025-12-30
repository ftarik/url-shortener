import string
import random
import qrcode
from io import BytesIO
from datetime import datetime, timedelta


def generate_short_code(length: int = 6) -> str:
    """Generate a random short code for URL shortening."""
    characters = string.ascii_letters + string.digits
    return ''.join(random.choice(characters) for _ in range(length))


def generate_qr_code(url: str) -> BytesIO:
    """Generate QR code for the given URL."""
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=10,
        border=4,
    )
    qr.add_data(url)
    qr.make(fit=True)

    img = qr.make_image(fill_color="black", back_color="white")
    
    # Save to BytesIO object
    buffer = BytesIO()
    img.save(buffer, format="PNG")
    buffer.seek(0)
    return buffer


def calculate_expiration_date(days: int) -> datetime:
    """Calculate expiration date from current time."""
    return datetime.utcnow() + timedelta(days=days)


def is_url_expired(expires_at: datetime) -> bool:
    """Check if URL has expired."""
    if expires_at is None:
        return False
    return datetime.utcnow() > expires_at
