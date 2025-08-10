# src/retrieval_service/views/upload.py

from flask import Blueprint, current_app, jsonify, request
from google.cloud import storage
import datetime

# This blueprint will handle all routes related to file uploads
upload_bp = Blueprint("upload_bp", __name__)

@upload_bp.route("/upload-gcs", methods=["POST"])
def upload_gcs():
    """Generates a signed URL for a GCS blob."""
    json_body = request.get_json(force=True)
    file_name = json_body.get("file_name")

    if not file_name:
        return jsonify({"error": "file_name is required"}), 400

    # Best practice: Use the app's config to get environment-specific settings
    gcs_bucket_name = current_app.config.get("GCS_BUCKET_NAME")
    if not gcs_bucket_name:
        # This provides a clear error in the logs if the environment variable is missing
        current_app.logger.error("GCS_BUCKET_NAME environment variable not set.")
        return jsonify({"error": "Server configuration error"}), 500

    try:
        storage_client = storage.Client()
        bucket = storage_client.bucket(gcs_bucket_name)
        blob = bucket.blob(file_name)

        # Generate the v4 signed URL
        signed_url = blob.generate_signed_url(
            version="v4",
            expiration=datetime.timedelta(minutes=15),
            method="PUT",
            content_type="application/octet-stream" # Recommended to specify content type
        )

        return jsonify({"signed_url": signed_url})

    except Exception as e:
        current_app.logger.error(f"Failed to generate signed URL: {e}")
        return jsonify({"error": "Failed to generate signed URL"}), 500