from flask import Blueprint, abort, render_template, request

from app.models import Vehicle

fleet_bp = Blueprint("fleet", __name__)


@fleet_bp.route("/fleet")
def list_vehicles():
    query = Vehicle.query.filter_by(is_active=True)
    category = request.args.get("category", "all")
    if category and category != "all":
        query = query.filter_by(category=category)
    min_seats = request.args.get("min_seats")
    if min_seats:
        query = query.filter(Vehicle.seats >= int(min_seats))
    ac = request.args.get("ac")
    if ac is not None and ac != "":
        query = query.filter(Vehicle.ac == (ac.lower() == "true"))
    vehicles = query.order_by(Vehicle.display_order).all()
    return render_template(
        "fleet.html",
        vehicles=vehicles,
        selected_category=category,
        title="Car & BUS | Rohit Transport",
        description="Browse our car and bus fleet with driver service.",
    )


@fleet_bp.route("/fleet/<slug>")
def vehicle_detail(slug):
    vehicle = Vehicle.query.filter_by(slug=slug, is_active=True).first()
    if not vehicle:
        abort(404)
    similar_vehicles = Vehicle.query.filter(
        Vehicle.id != vehicle.id,
        Vehicle.category == vehicle.category,
        Vehicle.is_active.is_(True),
    ).order_by(Vehicle.display_order).limit(3).all()
    return render_template(
        "vehicle.html",
        vehicle=vehicle,
        similar_vehicles=similar_vehicles,
        title=f"{vehicle.name} | Rohit Transport",
        description=f"Book a {vehicle.name} with driver. Premium vehicle rental in Ranchi, Muri and Silli.",
    )
