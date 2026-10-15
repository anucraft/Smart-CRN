"""Application factory: builds and wires the Flask app."""
import warnings

from flask import Flask, jsonify
from werkzeug.middleware.proxy_fix import ProxyFix

from .config import Config
from .extensions import cors, db, jwt


def create_app(config_object=Config):
    app = Flask(__name__)
    app.config.from_object(config_object)
    # Render/Vercel sit behind a proxy: trust X-Forwarded-* so request.url_root is https.
    app.wsgi_app = ProxyFix(app.wsgi_app, x_for=1, x_proto=1, x_host=1)
    # SQLite has no native Decimal; SQLAlchemy warns but stores values correctly.
    warnings.filterwarnings("ignore", message="Dialect sqlite.*does not support Decimal")

    db.init_app(app)
    jwt.init_app(app)
    cors.init_app(app, resources={r"/api/*": {"origins": app.config["CORS_ORIGINS"]}})

    from . import models  # noqa: F401  (registers tables)
    from .cli import register_cli
    from .routes import register_blueprints

    register_blueprints(app)
    register_cli(app)
    _register_error_handlers(app)

    @app.get("/api/health")
    def health():
        return jsonify({"status": "ok"})

    with app.app_context():
        db.create_all()  # MVP: creates missing tables on boot (see docs for Alembic as next step)
    return app


def _register_error_handlers(app):
    @app.errorhandler(404)
    def not_found(_):
        return jsonify({"error": "Not found."}), 404

    @app.errorhandler(405)
    def method_not_allowed(_):
        return jsonify({"error": "Method not allowed."}), 405

    @app.errorhandler(500)
    def server_error(_):
        return jsonify({"error": "Something went wrong on the server."}), 500

    # Make JWT failures use the same {"error": ...} shape; frontend treats 401 as "log in again".
    @jwt.unauthorized_loader
    def missing(msg):
        return jsonify({"error": "Authentication required."}), 401

    @jwt.invalid_token_loader
    def invalid(msg):
        return jsonify({"error": "Invalid token."}), 401

    @jwt.expired_token_loader
    def expired(header, payload):
        return jsonify({"error": "Session expired. Please log in again."}), 401
