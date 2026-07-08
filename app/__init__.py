from flask import Flask

from app.config import Config
from app.routes import main


def create_app() -> Flask:
    app = Flask(__name__)
    app.config.from_object(Config)

    app.register_blueprint(main)

    return app
