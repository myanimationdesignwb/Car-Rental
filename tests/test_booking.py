from app import create_app, db
from app.models import Booking, Vehicle


def setup_test_app():
    app = create_app(
        {
            "TESTING": True,
            "SQLALCHEMY_DATABASE_URI": "sqlite://",
            "WTF_CSRF_ENABLED": False,
            "SECRET_KEY": "test-secret",
        }
    )
    with app.app_context():
        db.drop_all()
        db.create_all()
        vehicle = Vehicle(
            name="Dzire",
            slug="dzire",
            category="car",
            seats=4,
            ac=True,
            fuel_type="Diesel",
            description="Test vehicle",
            features=["AC", "Driver included"],
            price_per_km=15,
            price_per_day=2200,
            min_km_per_day=80,
            driver_allowance_per_day=400,
            image_path="vehicles/dzire.jpg",
            is_active=True,
            display_order=1,
        )
        db.session.add(vehicle)
        db.session.commit()
        vehicle_id = vehicle.id
    return app, vehicle_id


def test_booking_creation_success():
    app, vehicle_id = setup_test_app()
    with app.test_client() as client:
        response = client.post(
            "/book",
            data={
                "trip_type": "local",
                "pickup_location": "Ranchi",
                "drop_location": "Jamshedpur",
                "pickup_date": "2026-12-12",
                "pickup_time": "09:00",
                "return_date": "",
                "vehicle_id": str(vehicle_id),
                "customer_name": "Rahul Kumar",
                "customer_phone": "9876543210",
                "customer_email": "rahul@example.com",
                "passengers": "4",
                "notes": "Need an airport transfer",
                "estimated_km": "120",
            },
            follow_redirects=False,
        )
        assert response.status_code == 302
        with app.app_context():
            booking = Booking.query.first()
            assert booking is not None
            assert booking.status == "pending"
            assert booking.booking_ref.startswith("RTT-")


def test_booking_rejects_invalid_mobile():
    app, vehicle_id = setup_test_app()
    with app.test_client() as client:
        response = client.post(
            "/book",
            data={
                "trip_type": "outstation",
                "pickup_location": "Ranchi",
                "drop_location": "Patna",
                "pickup_date": "2026-12-15",
                "pickup_time": "10:00",
                "vehicle_id": str(vehicle_id),
                "customer_name": "Test User",
                "customer_phone": "12345",
                "customer_email": "",
                "estimated_km": "150",
            },
            follow_redirects=True,
        )
        assert response.status_code == 200
        with app.app_context():
            assert Booking.query.count() == 0
