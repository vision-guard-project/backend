from flask import Flask
from dotenv import load_dotenv

from app.common.config import config
from app.controllers.api import create_api_blueprint
from app.infrastructure.extensions import init_extensions
from app.common.security.jwt_callbacks import register_jwt_callbacks


def create_app(config_object='dev'):
    app = Flask(__name__)
    app.config.from_object(config[config_object])

    init_extensions(app)

    return app
