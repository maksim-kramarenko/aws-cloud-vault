from flask import Flask

from app.config import Config
from app.extensions import db, migrate
from app.routes import main


def create_app(config_overrides: dict | None = None) -> Flask:
    app = Flask(__name__)
    app.config.from_object(Config)

    if config_overrides:
        app.config.update(config_overrides)

    db.init_app(app)
    migrate.init_app(app, db)

    app.register_blueprint(main)

    from app import models  # noqa: F401

    return app
