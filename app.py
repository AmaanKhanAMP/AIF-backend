"""AMP India Foundation — Flask API application factory."""

from pathlib import Path

from flask import Flask, jsonify, send_from_directory

from config import Config
from extensions import db, migrate, cors


def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)

    upload_root = Path(app.root_path) / "uploads"
    upload_root.mkdir(parents=True, exist_ok=True)
    app.config["UPLOAD_FOLDER"] = str(upload_root)

    db.init_app(app)
    migrate.init_app(app, db)
    cors.init_app(
        app,
        resources={r"/api/*": {"origins": app.config["CORS_ORIGINS"]}},
        supports_credentials=True,
    )

    # Models must be imported so Flask-Migrate can detect them
    from models import contact_message  # noqa: F401
    from models import cms_models  # noqa: F401
    from models import chat_message  # noqa: F401

    from routes.health_routes import health_bp
    from routes.contact_routes import contact_bp
    from routes.auth_routes import auth_bp
    from routes.content_routes import admin_content_bp, public_content_bp
    from routes.upload_routes import upload_bp
    from routes.admin_contact_routes import admin_contact_bp
    from routes.dashboard_routes import dashboard_bp
    from routes.chat_routes import chat_bp
    from routes.chatbot_sync_routes import chatbot_sync_bp

    app.register_blueprint(health_bp, url_prefix="/api")
    app.register_blueprint(contact_bp, url_prefix="/api/contact")
    app.register_blueprint(auth_bp, url_prefix="/api/auth")
    app.register_blueprint(admin_content_bp, url_prefix="/api/admin/content")
    app.register_blueprint(public_content_bp, url_prefix="/api/content")
    app.register_blueprint(upload_bp, url_prefix="/api/admin/upload")
    app.register_blueprint(admin_contact_bp, url_prefix="/api/admin/contact")
    app.register_blueprint(dashboard_bp, url_prefix="/api/admin/dashboard")
    app.register_blueprint(chat_bp, url_prefix="/api/chat")
    app.register_blueprint(chatbot_sync_bp, url_prefix="/api/admin/chatbot")

    # Warm the chatbot knowledge cache once at startup (Phase 2)
    try:
        from services.knowledge_loader import load_knowledge

        load_knowledge()
    except Exception:
        # Non-fatal — first chat request will retry loading
        pass

    @app.get("/uploads/<path:filepath>")
    def serve_uploads(filepath):
        return send_from_directory(app.config["UPLOAD_FOLDER"], filepath)

    @app.errorhandler(404)
    def not_found(_error):
        return jsonify({"success": False, "message": "Resource not found."}), 404

    @app.errorhandler(500)
    def server_error(_error):
        return jsonify({"success": False, "message": "Internal server error."}), 500

    return app


app = create_app()


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
