# Filename: src/retrieval_service/app/routes.py
import os
from datetime import timedelta
from flask import Blueprint, request, jsonify
from google.cloud import storage

# This is now the only required import at the top
from datastore.datastore import get_datastore

# Create a Blueprint, not a full app
routes = Blueprint('routes', __name__)

@routes.route("/documents/search", methods=["GET"])
def search():
    # ... (rest of the function is correct)
    query = request.args.get("query")
    top_k = request.args.get("top_k", 3)
    datastore = get_datastore()
    results = datastore.search(query=query, top_k=int(top_k))
    output = [doc.to_dict() for doc in results]
    return jsonify(output)

@routes.route("/documents/upload", methods=["POST"])
def upload():
    # Import Document model inside the function to avoid circular imports
    from models.models import Document
    # ... (rest of the function is correct)
    if "file" not in request.files:
        return {"error": "No file part"}, 400
    file = request.files["file"]
    if file.filename == "":
        return {"error": "No selected file"}, 400
    if file:
        datastore = get_datastore()
        doc = Document.from_file(file)
        datastore.upload(documents=[doc])
        return {"message": f"File {file.filename} uploaded successfully"}, 200
    return {"error": "File not allowed"}, 400

@routes.route("/documents/generate-upload-url", methods=["POST"])
def generate_upload_url():
    # ... (rest of the function is correct)
    bucket_name = os.environ.get("GCS_BUCKET_NAME")
    request_json = request.get_json()
    filename = request_json["filename"]
    storage_client = storage.Client()
    bucket = storage_client.bucket(bucket_name)
    blob = bucket.blob(filename)
    signed_url = blob.generate_signed_url(
        version="v4",
        expiration=timedelta(minutes=15),
        method="PUT",
        content_type="application/pdf",
    )
    return {"signedUrl": signed_url}, 200