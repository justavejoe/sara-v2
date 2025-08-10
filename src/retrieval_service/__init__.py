# src/retrieval_service/__init__.py

import os
from flask import Flask

def create_app():
    """
    Application factory function. Creates and configures the Flask app.
    This is the single entry point for creating the application.
    """
    app = Flask(__name__)

    # Securely load configuration from environment variables
    # This makes the app configurable without changing code.
    app.config["GCS_BUCKET_NAME"] = os.environ.get("GCS_BUCKET_NAME")
    # Add other configurations here if needed
    # app.config["DB_USER"] = os.environ.get("DB_USER")

    # The app context is the correct place to register all blueprints.
    with app.app_context():
        # Import blueprints here, inside the function, to avoid circular dependencies.
        from .main import main_bp
        from .views.upload import upload_bp

        # Register the blueprints with the app
        app.register_blueprint(main_bp)
        # We can add a URL prefix to all routes in this blueprint for better organization
        app.register_blueprint(upload_bp, url_prefix='/api')

    return app