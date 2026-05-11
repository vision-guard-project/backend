from flask import Blueprint


def create_api_blueprint():
    api_bp = Blueprint("api", __name__, url_prefix="/api")

    from app.controllers.auth_controller import auth_bp

    api_bp.register_blueprint(auth_bp)

    return api_bp
