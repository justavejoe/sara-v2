# src/retrieval_service/__init__.py

import os
from flask import Flask

def create_app():
    """
    Application factory function. Creates and configures the Flask app.
    """
    app = Flask(__name__)

    # Import and register the teardown function
    from . import db
    app.teardown_appcontext(db.close_db)

    # Import and register blueprints
    from .main import main_bp
    from .views.upload import upload_bp

    app.register_blueprint(main_bp)
    app.register_blueprint(upload_bp)

    return app