# src/retrieval_service/__init__.py
from flask import Flask

def create_app():
    """
    Application factory function.
    """
    app = Flask(__name__)

    # Import and register blueprints inside the factory
    with app.app_context():
        # Import your blueprints here
        # Example:
        # from . import main_routes
        # app.register_blueprint(main_routes.main)

        # For your existing structure, if you have a 'main' blueprint in main.py:
        from . import main
        app.register_blueprint(main.main)
        
        # If you have other blueprints in a 'views' directory:
        # from .views import upload
        # app.register_blueprint(upload.upload_bp)

    return app