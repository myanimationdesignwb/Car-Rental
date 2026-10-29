import os
from flask import Flask, render_template
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy
from flask_talisman import Talisman
from dotenv import load_dotenv

from app.config import Config

load_dotenv()


db = SQLAlchemy()
migrate = Migrate()
limiter = Limiter(key_func=get_remote_address, default_limits=["200/day", "50/hour"], storage_uri="memory://")
talisman = Talisman()


def create_app(test_config=None):
    app = Flask(__name__)
    app.config.from_object(Config)
    if test_config:
        app.config.update(test_config)

    db.init_app(app)
    migrate.init_app(app, db)
    limiter.init_app(app)
    talisman.init_app(app, content_security_policy=None, force_https=False)

    from app.routes.main import main_bp
    from app.routes.fleet import fleet_bp
    from app.routes.booking import booking_bp
    from app.routes.api import api_bp

    app.register_blueprint(main_bp)
    app.register_blueprint(fleet_bp)
    app.register_blueprint(booking_bp)
    app.register_blueprint(api_bp)

    with app.app_context():
        db.create_all()

    @app.errorhandler(404)
    def page_not_found(error):
        return render_template("404.html"), 404

    @app.errorhandler(500)
    def internal_server_error(error):
        return render_template("500.html"), 500

    return app
