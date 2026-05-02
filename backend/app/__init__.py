import logging
from logging.config import dictConfig

from flask import Flask, jsonify

from app.config import Config
from app.controllers.auth import auth_bp
from app.controllers.dashboard import dashboard_bp
from app.controllers.health import health_bp
from app.controllers.submissions import submissions_bp
from app.extensions import cors, db, jwt, limiter, migrate, socketio


def create_app(config_class=Config):
    configure_logging()
    app = Flask(__name__)
    app.config.from_object(config_class)

    db.init_app(app)
    migrate.init_app(app, db)
    jwt.init_app(app)
    cors.init_app(app, origins=app.config["CORS_ORIGINS"], supports_credentials=True)
    limiter.init_app(app)
    socketio.init_app(
        app,
        cors_allowed_origins=app.config["CORS_ORIGINS"],
        async_mode=app.config.get("SOCKETIO_ASYNC_MODE", "eventlet"),
    )

    app.register_blueprint(health_bp)
    app.register_blueprint(auth_bp, url_prefix="/api/auth")
    app.register_blueprint(submissions_bp, url_prefix="/api/submissions")
    app.register_blueprint(dashboard_bp, url_prefix="/api/dashboard")

    register_security_headers(app)
    register_error_handlers(app)

    with app.app_context():
        db.create_all()

    return app


def configure_logging():
    dictConfig(
        {
            "version": 1,
            "formatters": {
                "default": {
                    "format": "[%(asctime)s] %(levelname)s in %(module)s: %(message)s"
                }
            },
            "handlers": {
                "wsgi": {
                    "class": "logging.StreamHandler",
                    "formatter": "default",
                }
            },
            "root": {"level": "INFO", "handlers": ["wsgi"]},
        }
    )


def register_security_headers(app):
    @app.after_request
    def add_security_headers(response):
        response.headers.setdefault("X-Content-Type-Options", "nosniff")
        response.headers.setdefault("X-Frame-Options", "DENY")
        response.headers.setdefault("Referrer-Policy", "strict-origin-when-cross-origin")
        response.headers.setdefault("Permissions-Policy", "geolocation=(), microphone=(), camera=()")
        return response


def register_error_handlers(app):
    @app.errorhandler(400)
    def bad_request(error):
        return jsonify({"error": "bad_request", "message": str(error)}), 400

    @app.errorhandler(404)
    def not_found(error):
        return jsonify({"error": "not_found", "message": "Resource not found"}), 404

    @app.errorhandler(429)
    def rate_limited(error):
        return jsonify({"error": "rate_limited", "message": "Too many requests"}), 429

    @app.errorhandler(Exception)
    def internal_error(error):
        app.logger.exception("Unhandled application error: %s", error)
        return jsonify({"error": "internal_error", "message": "Unexpected server error"}), 500
