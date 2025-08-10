# src/retrieval_service/__init__.py

import os
import logging
from flask import Flask

# --- Configure Logging ---
# This sets up logging to output detailed information to the console (Cloud Run logs)
logging.basicConfig(level=logging.INFO)

def create_app():
    """
    Application factory function. Creates and configures the Flask app.
    """
    logging.info("Starting create_app function...")
    app = Flask(__name__)
    logging.info("Flask app created.")

    # Load configuration from environment variables
    app.config["GCS_BUCKET_NAME"] = os.environ.get("GCS_BUCKET_NAME")
    logging.info("Configuration loaded.")

    with app.app_context():
        logging.info("Entering app context to register blueprints.")
        
        # Import blueprints here to avoid circular dependencies
        from .main import main_bp
        from .views.upload import upload_bp
        logging.info("Blueprints imported successfully.")

        # Register the blueprints with the app
        app.register_blueprint(main_bp)
        logging.info("main_bp registered.")
        app.register_blueprint(upload_bp, url_prefix='/api')
        logging.info("upload_bp registered.")

    logging.info("create_app function finished successfully.")
    return app