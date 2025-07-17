import os
import requests
import google.auth.transport.requests
import google.oauth2.id_token
from fastapi import FastAPI, Request
from fastapi.responses import FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles

app = FastAPI()

# This is the URL of our private backend service
BACKEND_URL = os.environ.get("SERVICE_URL")

# Serve static files like CSS and JS
app.mount("/static", StaticFiles(directory="static"), name="static")

# Serve the main HTML page
@app.get("/")
async def read_index():
    return FileResponse('templates/index.html')

# This is our new proxy endpoint
@app.get("/api/search")
async def search_proxy(query: str, top_k: int = 3):
    if not BACKEND_URL:
        return JSONResponse(status_code=500, content={"message": "Backend service URL not configured."})

    try:
        # Get an identity token for the backend service
        auth_req = google.auth.transport.requests.Request()
        id_token = google.oauth2.id_token.fetch_id_token(auth_req, BACKEND_URL)

        headers = {"Authorization": f"Bearer {id_token}"}

        # Make the secure, server-to-server request
        search_url = f"{BACKEND_URL}/documents/search?query={query}&top_k={top_k}"
        response = requests.get(search_url, headers=headers)
        response.raise_for_status() # Raise an exception for bad status codes

        return JSONResponse(content=response.json())

    except Exception as e:
        return JSONResponse(status_code=500, content={"message": f"Error communicating with backend: {e}"})