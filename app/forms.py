from flask_wtf import FlaskForm
from wtforms import DateField, HiddenField, IntegerField, SelectField, StringField, SubmitField, TextAreaField
from wtforms.validators import DataRequired, Email, NumberRange, Optional, Regexp


class BookingForm(FlaskForm):
    trip_type = SelectField(
        "Trip type",
        choices=[
            ("local", "Local Rental"),
            ("outstation", "Outstation"),
            ("airport", "Airport Transfer"),
            ("wedding", "Wedding / Events"),
            ("goods", "Goods Transport"),
            ("other", "Other"),
        ],
        validators=[DataRequired()],
    )
    pickup_location = StringField("Pickup location", validators=[DataRequired()])
    drop_location = StringField("Drop location", validators=[DataRequired()])
    pickup_date = DateField("Pickup date", format="%Y-%m-%d", validators=[DataRequired()])
    pickup_time = StringField("Pickup time", validators=[DataRequired()])
    return_date = DateField("Return date", format="%Y-%m-%d", validators=[Optional()])
    vehicle_id = SelectField("Vehicle", coerce=int, validators=[DataRequired()])
    customer_name = StringField("Full name", validators=[DataRequired()])
    customer_phone = StringField(
        "Phone number",
        validators=[
            DataRequired(),
            Regexp(r"^[6-9]\d{9}$", message="Enter a valid 10-digit Indian mobile number."),
        ],
    )
    customer_email = StringField("Email (optional)", validators=[Optional(), Email()])
    passengers = IntegerField("Passengers", validators=[Optional(), NumberRange(min=1)])
    notes = TextAreaField("Notes")
    estimated_km = IntegerField("Estimated distance (km)", validators=[Optional(), NumberRange(min=1)])
    honeypot = HiddenField()
    submit = SubmitField("Submit booking")


class TrackBookingForm(FlaskForm):
    booking_ref = StringField("Booking reference", validators=[DataRequired()])
    customer_phone = StringField(
        "Phone number",
        validators=[
            DataRequired(),
            Regexp(r"^[6-9]\d{9}$", message="Enter a valid 10-digit Indian mobile number."),
        ],
    )
    honeypot = HiddenField()
    submit = SubmitField("Track booking")


class ContactForm(FlaskForm):
    name = StringField("Your name", validators=[DataRequired()])
    phone = StringField(
        "Phone",
        validators=[
            DataRequired(),
            Regexp(r"^[6-9]\d{9}$", message="Enter a valid 10-digit Indian mobile number."),
        ],
    )
    message = TextAreaField("Message", validators=[DataRequired()])
    submit = SubmitField("Send enquiry")
