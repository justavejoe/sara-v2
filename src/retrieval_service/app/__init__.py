# Filename: src/retrieval_service/app/__init__.py

from flask import Flask

# Create the main Flask app object
app = Flask(__name__)

# Import the routes Blueprint AFTER the app is created
from . import routes

# Register the routes with the main application
app.register_blueprint(routes.routes)