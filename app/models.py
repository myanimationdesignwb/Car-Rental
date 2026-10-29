from datetime import datetime

from app import db


class Vehicle(db.Model):
    __tablename__ = "vehicles"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), nullable=False)
    slug = db.Column(db.String(120), unique=True, nullable=False)
    category = db.Column(db.String(20), nullable=False)
    seats = db.Column(db.Integer, nullable=True)
    capacity_note = db.Column(db.String(100), nullable=True)
    ac = db.Column(db.Boolean, default=True)
    fuel_type = db.Column(db.String(50), nullable=True)
    description = db.Column(db.Text, nullable=False)
    features = db.Column(db.JSON, default=list)
    price_per_km = db.Column(db.Float, default=0.0)
    price_per_day = db.Column(db.Float, default=0.0)
    min_km_per_day = db.Column(db.Integer, default=100)
    driver_allowance_per_day = db.Column(db.Float, default=0.0)
    image_path = db.Column(db.String(255), nullable=False, default="images/vehicles/placeholder.jpg")
    is_active = db.Column(db.Boolean, default=True)
    display_order = db.Column(db.Integer, default=0)


class Booking(db.Model):
    __tablename__ = "bookings"
    id = db.Column(db.Integer, primary_key=True)
    booking_ref = db.Column(db.String(30), unique=True, nullable=False)
    customer_name = db.Column(db.String(120), nullable=False)
    customer_phone = db.Column(db.String(20), nullable=False)
    customer_email = db.Column(db.String(120), nullable=True)
    vehicle_id = db.Column(db.Integer, db.ForeignKey("vehicles.id"), nullable=False)
    trip_type = db.Column(db.String(30), nullable=False)
    pickup_location = db.Column(db.String(200), nullable=False)
    drop_location = db.Column(db.String(200), nullable=False)
    pickup_date = db.Column(db.Date, nullable=False)
    pickup_time = db.Column(db.String(20), nullable=False)
    return_date = db.Column(db.Date, nullable=True)
    passengers = db.Column(db.Integer, nullable=True)
    notes = db.Column(db.Text, nullable=True)
    estimated_fare = db.Column(db.Float, nullable=True)
    status = db.Column(db.String(20), default="pending", nullable=False)
    admin_note = db.Column(db.Text, nullable=True)
    notified_at = db.Column(db.DateTime, nullable=True)
    notify_error = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    vehicle = db.relationship("Vehicle", backref="bookings")


class Enquiry(db.Model):
    __tablename__ = "enquiries"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), nullable=False)
    phone = db.Column(db.String(20), nullable=False)
    message = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    is_resolved = db.Column(db.Boolean, default=False)


class Review(db.Model):
    __tablename__ = "reviews"
    id = db.Column(db.Integer, primary_key=True)
    customer_name = db.Column(db.String(120), nullable=False)
    rating = db.Column(db.Integer, nullable=False)
    comment = db.Column(db.Text, nullable=False)
    is_approved = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)


class Setting(db.Model):
    __tablename__ = "settings"
    id = db.Column(db.Integer, primary_key=True)
    key = db.Column(db.String(120), unique=True, nullable=False)
    value = db.Column(db.Text, nullable=True)


def get_setting(key, default=None):
    row = Setting.query.filter_by(key=key).first()
    if row is None:
        return default
    return row.value


def get_json_setting(key, default=None):
    value = get_setting(key, default)
    if value is None:
        return default
    if isinstance(value, (dict, list)):
        return value
    import json
    try:
        return json.loads(value)
    except (TypeError, ValueError):
        return default
