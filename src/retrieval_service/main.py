# src/retrieval_service/main.py

from flask import Blueprint

# This file now only defines a blueprint for the main routes.
main_bp = Blueprint("main_bp", __name__)

@main_bp.route("/")
def index():
    """Health check endpoint."""
    return "Retrieval service is running."