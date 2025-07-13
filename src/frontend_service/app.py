from fastapi import FastAPI
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

app = FastAPI()

# Serve static files like CSS and JS
app.mount("/static", StaticFiles(directory="static"), name="static")

# Serve the main HTML page
@app.get("/")
async def read_index():
    return FileResponse('templates/index.html')