# src/retrieval_service/__init__.py

from flask import Flask
import os

def create_app():
    """
    Application factory function. Creates and configures the Flask app.
    """
    app = Flask(__name__)

    # Load environment variables into the app's config
    app.config["GCS_BUCKET_NAME"] = os.environ.get("GCS_BUCKET_NAME")


    # Register all blueprints within the application context
    with app.app_context():
        # Import blueprints here to avoid circular dependencies
        from .main import main_bp
        from .views.upload import upload_bp

        # Register the blueprints with the app
        app.register_blueprint(main_bp)
        app.register_blueprint(upload_bp, url_prefix='/api') # Optional: prefix all upload routes with /api

    return app