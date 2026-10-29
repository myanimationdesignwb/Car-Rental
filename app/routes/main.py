from flask import Blueprint, current_app, render_template

from app.forms import ContactForm
from app.models import Vehicle, get_json_setting

main_bp = Blueprint("main", __name__)


@main_bp.route("/")
def index():
    featured = Vehicle.query.filter_by(is_active=True).order_by(Vehicle.display_order).all()
    route_fares = get_json_setting(
        "route_fares",
        {
            "Ranchi to Jamshedpur": 2400,
            "Ranchi to Netarhat": 3200,
            "Ranchi to Deoghar": 3100,
            "Ranchi to Patna": 5700,
        },
    )
    return render_template(
        "home.html",
        featured_vehicles=featured,
        route_fares=route_fares,
        title="Car Rental in Ranchi | Rohit Transport",
        description="Premium taxi and vehicle rental service in Ranchi, Muri and Silli with driver included.",
    )


@main_bp.route("/about")
def about():
    return render_template("about.html", title="About Us | Rohit Transport", description="Learn more about Rohit Transport, Tour and Travels.")


@main_bp.route("/locations")
def locations():
    return render_template("locations.html", title="Locations | Rohit Transport", description="Ranchi, Muri and Silli taxi service and local travel routes.")


@main_bp.route("/contact")
def contact():
    form = ContactForm()
    return render_template(
        "contact.html",
        form=form,
        title="Contact | Rohit Transport",
        description="Contact Rohit Transport for bookings, tours, and logistics.",
    )


@main_bp.route("/terms")
def terms():
    return render_template("terms.html", title="Terms & Cancellation Policy | Rohit Transport")


@main_bp.route("/privacy")
def privacy_policy():
    return render_template("privacy.html", title="Privacy Policy | Rohit Transport")


@main_bp.route("/robots.txt")
def robots_txt():
    return "User-agent: *\nAllow: /\nSitemap: %s/sitemap.xml\n" % current_app.config.get("SITE_URL", "http://localhost:5000"), 200, {"Content-Type": "text/plain; charset=utf-8"}


@main_bp.route("/sitemap.xml")
def sitemap_xml():
    pages = [
        "",
        "/fleet",
        "/book",
        "/track",
        "/locations",
        "/about",
        "/contact",
        "/terms",
        "/privacy",
    ]
    base_url = current_app.config.get("SITE_URL", "http://localhost:5000")
    urls = "\n".join(f"<url><loc>{base_url}{p}</loc></url>" for p in pages)
    return "<?xml version='1.0' encoding='UTF-8'?><urlset xmlns='http://www.sitemaps.org/schemas/sitemap/0.9'>%s</urlset>" % urls, 200, {"Content-Type": "application/xml; charset=utf-8"}
