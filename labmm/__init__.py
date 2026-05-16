import os

from flask import Flask

from labmm.config import config_map
from flask_cors import CORS

from labmm.extensions import db, jwt, ma, migrate


def create_app(env: str | None = None) -> Flask:
    if env is None:
        env = os.environ.get("FLASK_ENV", "development")

    app = Flask(__name__)
    app.config.from_object(config_map[env])

    # Extensions
    CORS(app, origins=["http://localhost:4200"])
    db.init_app(app)
    migrate.init_app(app, db)
    jwt.init_app(app)
    ma.init_app(app)

    # Import models so Flask-Migrate detects them
    with app.app_context():
        from labmm import models  # noqa: F401

    # Error handlers
    from labmm.utils.errors import register_error_handlers
    register_error_handlers(app)

    # Blueprints
    from labmm.routes import register_blueprints
    register_blueprints(app)

    return app
