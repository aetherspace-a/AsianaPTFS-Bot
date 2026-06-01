"""Generate PNG boarding passes with Pillow + QR codes."""

import json
from pathlib import Path
from uuid import UUID

import qrcode
from PIL import Image, ImageDraw, ImageFont

from app.core.branding import load_branding
from app.core.config import get_settings
from app.models.booking import Booking, SeatClass
from app.models.flight import Flight
from app.models.user import User

settings = get_settings()

PASS_WIDTH = 900
PASS_HEIGHT = 420


def _hex_to_rgb(hex_color: str) -> tuple[int, int, int]:
    h = hex_color.lstrip("#")
    return tuple(int(h[i : i + 2], 16) for i in (0, 2, 4))


def _load_font(size: int, bold: bool = False) -> ImageFont.FreeTypeFont | ImageFont.ImageFont:
    candidates = (
        ["arialbd.ttf", "Arial Bold.ttf", "DejaVuSans-Bold.ttf"]
        if bold
        else ["arial.ttf", "Arial.ttf", "DejaVuSans.ttf"]
    )
    for name in candidates:
        try:
            return ImageFont.truetype(name, size)
        except OSError:
            continue
    return ImageFont.load_default()


def _class_color(seat_class: SeatClass) -> tuple[int, int, int]:
    if seat_class == SeatClass.FIRST:
        return (201, 162, 39)
    if seat_class == SeatClass.BUSINESS:
        return (180, 180, 200)
    return (200, 200, 200)


def generate_boarding_pass(
    booking: Booking,
    user: User,
    flight: Flight,
) -> Path:
    """Render boarding pass PNG; returns absolute path to file."""
    branding = load_branding()
    primary = _hex_to_rgb(branding.colors.primary)
    secondary = _hex_to_rgb(branding.colors.secondary)
    accent = _hex_to_rgb(branding.colors.accent)
    text_color = (245, 245, 247)
    muted = (156, 163, 175)

    out_dir = Path(settings.boarding_passes_path)
    out_dir.mkdir(parents=True, exist_ok=True)
    out_path = out_dir / f"{booking.id}.png"

    img = Image.new("RGB", (PASS_WIDTH, PASS_HEIGHT), secondary)
    draw = ImageDraw.Draw(img)

    draw.rectangle([0, 0, PASS_WIDTH, 72], fill=primary)
    title_font = _load_font(28, bold=True)
    sub_font = _load_font(16)
    label_font = _load_font(13)
    value_font = _load_font(22, bold=True)
    small_font = _load_font(12)

    draw.text((24, 20), branding.airline_name.upper(), fill=text_color, font=title_font)
    draw.text((24, 52), "BOARDING PASS", fill=accent, font=sub_font)

    # QR payload
    qr_payload = json.dumps(
        {
            "booking_id": str(booking.id),
            "flight": flight.flight_number,
            "seat": booking.seat_number,
            "passenger": user.username,
            "class": booking.seat_class.value,
        },
        separators=(",", ":"),
    )
    qr = qrcode.QRCode(version=1, box_size=4, border=2)
    qr.add_data(qr_payload)
    qr.make(fit=True)
    qr_img = qr.make_image(fill_color="black", back_color="white").convert("RGB")
    qr_img = qr_img.resize((140, 140))
    img.paste(qr_img, (PASS_WIDTH - 164, PASS_HEIGHT - 164))

    y = 96
    fields = [
        ("PASSENGER", user.username),
        ("FLIGHT", flight.flight_number),
        ("FROM / TO", f"{flight.departure}  →  {flight.arrival}"),
        ("CLASS", booking.seat_class.value),
        ("SEAT", booking.seat_number),
    ]
    if flight.aircraft:
        fields.append(("AIRCRAFT", flight.aircraft))

    col_w = (PASS_WIDTH - 200) // 2
    for i, (label, value) in enumerate(fields):
        col = i % 2
        row = i // 2
        x = 24 + col * col_w
        fy = y + row * 72
        draw.text((x, fy), label, fill=muted, font=label_font)
        draw.text((x, fy + 18), value, fill=text_color, font=value_font)

    # Class badge
    badge_y = PASS_HEIGHT - 48
    draw.rounded_rectangle(
        [24, badge_y, 180, badge_y + 28],
        radius=6,
        fill=_class_color(booking.seat_class),
    )
    draw.text((36, badge_y + 6), booking.seat_class.value.upper(), fill=(20, 20, 30), font=label_font)

    dep = flight.departure_time.strftime("%d %b %Y  %H:%M") if flight.departure_time else "—"
    draw.text((24, PASS_HEIGHT - 24), f"Departs {dep}  ·  ID {str(booking.id)[:8].upper()}", fill=muted, font=small_font)

    # Perforated edge
    for x in range(0, PASS_WIDTH, 16):
        draw.ellipse([x, 68, x + 6, 74], fill=(15, 15, 20))

    img.save(out_path, format="PNG", optimize=True)
    return out_path
