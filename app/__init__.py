from flask import Flask
from app.config import Config
from app.extensions import db, migrate, cors, jwt

from app.routes.auth_routes import auth_bp
from app.routes.admin_routes import admin_bp
from app.routes.cctv_routes import cctv_bp


def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    db.init_app(app)
    migrate.init_app(app, db)
    jwt.init_app(app)

    cors.init_app(
        app,
        resources={r"/api/*": {"origins": app.config["FRONTEND_URL"]}},
        supports_credentials=True,
    )

    app.register_blueprint(auth_bp, url_prefix="/api/auth")
    app.register_blueprint(admin_bp, url_prefix="/api/admin")
    app.register_blueprint(cctv_bp, url_prefix="/api/cctv")

    return app