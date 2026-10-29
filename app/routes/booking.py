from datetime import datetime

from flask import Blueprint, flash, redirect, render_template, request, url_for

from app import db
from app.forms import BookingForm, ContactForm, TrackBookingForm
from app.models import Booking, Enquiry, Vehicle
from app.notifications import build_booking_whatsapp_url, schedule_booking_notification

booking_bp = Blueprint("booking", __name__)


def generate_booking_ref():
    current_year = datetime.utcnow().year
    prefix = f"RTT-{current_year}-"
    last = Booking.query.filter(Booking.booking_ref.like(f"{prefix}%")).count() + 1
    return f"{prefix}{last:05d}"


@booking_bp.route("/book", methods=["GET", "POST"])
def book_ride():
    form = BookingForm()
    form.vehicle_id.choices = [(v.id, v.name) for v in Vehicle.query.filter_by(is_active=True).order_by(Vehicle.display_order).all()]

    if request.args.get("pickup"):
        form.pickup_location.data = request.args.get("pickup")
    if request.args.get("drop"):
        form.drop_location.data = request.args.get("drop")
    if request.args.get("trip_date"):
        form.pickup_date.data = datetime.strptime(request.args.get("trip_date"), "%Y-%m-%d").date()
    if request.args.get("vehicle"):
        form.vehicle_id.data = int(request.args.get("vehicle"))

    if form.validate_on_submit():
        if form.honeypot.data:
            flash("Request rejected.", "error")
            return redirect(url_for("booking.book_ride"))

        vehicle = Vehicle.query.get(form.vehicle_id.data)
        if vehicle is None:
            flash("Please choose a valid vehicle.", "error")
            return render_template("book.html", form=form, title="Book a Ride | Rohit Transport")

        distance_km = form.estimated_km.data or 100
        estimated = round(vehicle.price_per_km * distance_km, 2)
        booking = Booking(
            booking_ref=generate_booking_ref(),
            customer_name=form.customer_name.data,
            customer_phone=form.customer_phone.data,
            customer_email=form.customer_email.data,
            vehicle_id=vehicle.id,
            trip_type=form.trip_type.data,
            pickup_location=form.pickup_location.data,
            drop_location=form.drop_location.data,
            pickup_date=form.pickup_date.data,
            pickup_time=form.pickup_time.data,
            return_date=form.return_date.data,
            passengers=form.passengers.data,
            notes=form.notes.data,
            estimated_fare=estimated,
            status="pending",
        )
        db.session.add(booking)
        db.session.commit()

        schedule_booking_notification(booking)
        whatsapp_url = build_booking_whatsapp_url(booking)
        return redirect(whatsapp_url)

    return render_template("book.html", form=form, title="Book a Ride | Rohit Transport")


@booking_bp.route("/book/confirmation/<booking_ref>")
def booking_success(booking_ref):
    booking = Booking.query.filter_by(booking_ref=booking_ref).first_or_404()
    whatsapp_url = build_booking_whatsapp_url(booking)
    return render_template(
        "booking_success.html",
        booking=booking,
        whatsapp_url=whatsapp_url,
        title="Booking Confirmed | Rohit Transport",
    )


@booking_bp.route("/track", methods=["GET", "POST"])
def track_booking():
    form = TrackBookingForm()
    booking = None
    if form.validate_on_submit():
        if form.honeypot.data:
            flash("Please try again.", "error")
        else:
            booking = Booking.query.filter_by(
                booking_ref=form.booking_ref.data,
                customer_phone=form.customer_phone.data,
            ).first()
            if booking is None:
                flash("Booking not found. Please check your details.", "error")
    return render_template("track.html", form=form, booking=booking, title="Track Your Booking | Rohit Transport")


@booking_bp.route("/contact", methods=["POST"])
def submit_contact():
    form = ContactForm()
    if form.validate_on_submit():
        enquiry = Enquiry(
            name=form.name.data,
            phone=form.phone.data,
            message=form.message.data,
            is_resolved=False,
        )
        db.session.add(enquiry)
        db.session.commit()
        flash("Your enquiry has been received. We will contact you shortly.", "success")
        return redirect(url_for("main.contact"))
    flash("Please correct the highlighted fields and try again.", "error")
    return redirect(url_for("main.contact"))
