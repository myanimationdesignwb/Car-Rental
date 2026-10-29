import json
import os
import threading
from datetime import datetime
import logging
from urllib.parse import quote

import requests
from flask import current_app
from twilio.rest import Client

logger = logging.getLogger(__name__)


def _owner_whatsapp_number():
    return current_app.config.get("OWNER_WHATSAPP", "919608576670")


def _normalize_whatsapp_number(raw_number):
    digits = "".join(ch for ch in (raw_number or "919608576670") if ch.isdigit())
    if len(digits) == 10:
        return "91" + digits
    if len(digits) == 12 and digits.startswith("91"):
        return digits
    if len(digits) == 11 and digits.startswith("0"):
        return "91" + digits[1:]
    return digits


def format_booking_whatsapp_message(booking):
    vehicle_name = booking.vehicle.name if booking.vehicle else "Not selected"
    trip_type = booking.trip_type or "Trip"
    pickup_date = booking.pickup_date.strftime("%d %b %Y") if booking.pickup_date else "Not specified"
    pickup_time = booking.pickup_time or "Not specified"
    return (
        "Hi Rohit Transport,\n\n"
        "I want to book a ride. Please confirm the fare and availability.\n\n"
        "*Booking Details*\n"
        f"Booking Ref: {booking.booking_ref}\n"
        f"Customer Name: {booking.customer_name}\n"
        f"Phone: {booking.customer_phone}\n"
        f"Email: {booking.customer_email or 'Not provided'}\n"
        f"Vehicle: {vehicle_name}\n"
        f"Trip Type: {trip_type}\n"
        f"Route: {booking.pickup_location} to {booking.drop_location}\n"
        f"Pickup Date: {pickup_date}\n"
        f"Pickup Time: {pickup_time}\n"
        f"Passengers: {booking.passengers or 'Not specified'}\n"
        f"Estimated Fare: ₹{booking.estimated_fare or 'Not available'}\n"
        f"Notes: {booking.notes or 'No extra notes'}\n\n"
        "Please share the final price and confirm the trip."
    )


def build_booking_whatsapp_url(booking):
    message = format_booking_whatsapp_message(booking)
    number = _normalize_whatsapp_number(_owner_whatsapp_number())
    return f"https://wa.me/{number}?text={quote(message)}"


def _send_meta_whatsapp_text(message, recipient_number):
    token = os.getenv("WHATSAPP_TOKEN")
    phone_number_id = os.getenv("WHATSAPP_PHONE_NUMBER_ID")
    if not token or not phone_number_id:
        raise RuntimeError("Meta WhatsApp not configured")

    payload = {
        "messaging_product": "whatsapp",
        "to": _normalize_whatsapp_number(recipient_number),
        "type": "text",
        "text": {"body": message},
    }

    response = requests.post(
        f"https://graph.facebook.com/v18.0/{phone_number_id}/messages",
        headers={"Authorization": f"Bearer {token}", "Content-Type": "application/json"},
        data=json.dumps(payload),
        timeout=20,
    )
    if response.status_code >= 400:
        raise RuntimeError(response.text)
    return True


def _send_meta_whatsapp(booking):
    token = os.getenv("WHATSAPP_TOKEN")
    phone_number_id = os.getenv("WHATSAPP_PHONE_NUMBER_ID")
    if not token or not phone_number_id:
        raise RuntimeError("Meta WhatsApp not configured")
    payload = {
        "messaging_product": "whatsapp",
        "to": _owner_whatsapp_number(),
        "type": "template",
        "template": {
            "name": "booking_notification",
            "language": {"code": "en_US"},
            "components": [{
                "type": "body",
                "parameters": [
                    {"type": "text", "text": booking.booking_ref},
                    {"type": "text", "text": booking.customer_name},
                    {"type": "text", "text": booking.customer_phone},
                    {"type": "text", "text": booking.vehicle.name},
                    {"type": "text", "text": booking.trip_type},
                    {"type": "text", "text": f"{booking.pickup_location} to {booking.drop_location}"},
                    {"type": "text", "text": booking.pickup_date.strftime("%d %b %Y")},
                    {"type": "text", "text": f"{current_app.config.get('SITE_URL', 'http://localhost:5000')}/admin/bookings/{booking.booking_ref}"},
                ]
            }]
        }
    }
    response = requests.post(
        f"https://graph.facebook.com/v18.0/{phone_number_id}/messages",
        headers={"Authorization": f"Bearer {token}", "Content-Type": "application/json"},
        data=json.dumps(payload),
        timeout=20,
    )
    if response.status_code >= 400:
        raise RuntimeError(response.text)


def _send_twilio_whatsapp(message, recipient_number):
    sid = os.getenv("TWILIO_ACCOUNT_SID")
    token = os.getenv("TWILIO_AUTH_TOKEN")
    from_number = os.getenv("TWILIO_WHATSAPP_NUMBER")
    if not sid or not token or not from_number:
        raise RuntimeError("Twilio WhatsApp not configured")
    client = Client(sid, token)
    client.messages.create(body=message, from_=f"whatsapp:{from_number}", to=f"whatsapp:{recipient_number}")


def _send_email(subject, message, recipient_email):
    host = os.getenv("SMTP_HOST")
    username = os.getenv("SMTP_USERNAME")
    password = os.getenv("SMTP_PASSWORD")
    if not host or not username or not password:
        raise RuntimeError("SMTP not configured")
    import smtplib
    from email.message import EmailMessage

    msg = EmailMessage()
    msg["Subject"] = subject
    msg["From"] = username
    msg["To"] = recipient_email
    msg.set_content(message)
    with smtplib.SMTP(host, int(os.getenv("SMTP_PORT", "587"))) as server:
        if os.getenv("SMTP_USE_TLS", "True").lower() in {"1", "true", "yes"}:
            server.starttls()
        server.login(username, password)
        server.send_message(msg)


def _send_telegram(message):
    token = os.getenv("TELEGRAM_BOT_TOKEN")
    chat_id = os.getenv("TELEGRAM_CHAT_ID")
    if not token or not chat_id:
        raise RuntimeError("Telegram not configured")
    response = requests.get(
        f"https://api.telegram.org/bot{token}/sendMessage",
        params={"chat_id": chat_id, "text": message},
        timeout=20,
    )
    if response.status_code >= 400:
        raise RuntimeError(response.text)


def _notify_owner(booking):
    owner_number = _owner_whatsapp_number()
    text = format_booking_whatsapp_message(booking)

    for method in ["meta", "twilio", "email", "telegram"]:
        try:
            if method == "meta":
                _send_meta_whatsapp_text(text, owner_number)
            elif method == "twilio":
                _send_twilio_whatsapp(text, owner_number)
            elif method == "email":
                _send_email("New booking request", text, current_app.config.get("OWNER_EMAIL", "owner@example.com"))
            elif method == "telegram":
                _send_telegram(text)
            return True
        except Exception:
            logger.exception("Notification failed via %s", method)
    return False


def _send_customer_acknowledgement(booking):
    message = (
        f"Hello {booking.customer_name}, we have received your booking request {booking.booking_ref}. "
        "Our team will confirm the ride shortly."
    )
    try:
        _send_twilio_whatsapp(message, booking.customer_phone)
        return True
    except Exception:
        logger.exception("Customer acknowledgement failed")
        return False


def send_booking_notification(booking):
    try:
        owner_sent = _notify_owner(booking)
        customer_sent = _send_customer_acknowledgement(booking)
        booking.notified_at = datetime.utcnow()
        booking.notify_error = None if owner_sent or customer_sent else "Notification delivery failed"
    except Exception as exc:
        booking.notified_at = datetime.utcnow()
        booking.notify_error = str(exc)
        logger.exception("Booking notification failed")


def schedule_booking_notification(booking):
    app = current_app._get_current_object()

    def _run():
        with app.app_context():
            send_booking_notification(booking)

    thread = threading.Thread(target=_run, daemon=True)
    thread.start()
    return thread
