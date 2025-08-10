# src/retrieval_service/main.py

from flask import Blueprint

# This file now only defines a blueprint for the main routes.
# The actual Flask app is created in the __init__.py file.
main = Blueprint("main", __name__)

@main.route("/")
def index():
    """Health check endpoint."""
    return "Retrieval service is running."

# NOTE: You can add other simple, top-level routes to this file.
# More complex sets of routes (like for handling documents or uploads)
# should be in their own separate blueprint files for better organization.