# Filename: src/retrieval_service/app/app.py

from flask import Flask

# Import the Blueprint we created in routes.py
from .routes import routes

# Create the main Flask app object
app = Flask(__name__)

# Register our routes with the main application
app.register_blueprint(routes)