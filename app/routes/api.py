from flask import Blueprint, jsonify

from app.models import Vehicle

api_bp = Blueprint("api", __name__)


@api_bp.route("/api/vehicles")
def vehicles_api():
    items = []
    for vehicle in Vehicle.query.filter_by(is_active=True).order_by(Vehicle.display_order).all():
        items.append(
            {
                "id": vehicle.id,
                "name": vehicle.name,
                "slug": vehicle.slug,
                "category": vehicle.category,
                "seats": vehicle.seats,
                "price_per_km": vehicle.price_per_km,
                "price_per_day": vehicle.price_per_day,
                "image_path": vehicle.image_path,
            }
        )
    return jsonify(items)
