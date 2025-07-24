import os
import requests
import google.auth.transport.requests
import google.oauth2.id_token
from fastapi import FastAPI, Request, UploadFile, File
from fastapi.responses import FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from typing import List

app = FastAPI()

BACKEND_URL = os.environ.get("SERVICE_URL")

app.mount("/static", StaticFiles(directory="static"), name="static")

@app.get("/")
async def read_index():
    return FileResponse('templates/index.html')

def get_id_token():
    """Helper function to get a Google-signed ID token."""
    auth_req = google.auth.transport.requests.Request()
    id_token = google.oauth2.id_token.fetch_id_token(auth_req, BACKEND_URL)
    return id_token

@app.get("/api/search")
async def search_proxy(query: str, top_k: int = 3):
    if not BACKEND_URL:
        return JSONResponse(status_code=500, content={"message": "Backend service URL not configured."})
    try:
        headers = {"Authorization": f"Bearer {get_id_token()}"}
        search_url = f"{BACKEND_URL}/documents/search?query={query}&top_k={top_k}"
        response = requests.get(search_url, headers=headers)
        response.raise_for_status()
        return JSONResponse(content=response.json())
    except Exception as e:
        return JSONResponse(status_code=500, content={"message": f"Error communicating with backend: {e}"})

@app.post("/api/upload")
async def upload_proxy(files: List[UploadFile] = File(...)):
    if not BACKEND_URL:
        return JSONResponse(status_code=500, content={"message": "Backend service URL not configured."})
    try:
        headers = {"Authorization": f"Bearer {get_id_token()}"}
        upload_url = f"{BACKEND_URL}/documents/upload"
        
        file_list = [("files", (file.filename, file.file, file.content_type)) for file in files]
        
        response = requests.post(upload_url, headers=headers, files=file_list)
        response.raise_for_status()
        
        return JSONResponse(content=response.json())
    except Exception as e:
        return JSONResponse(status_code=500, content={"message": f"Error communicating with backend: {e}"})