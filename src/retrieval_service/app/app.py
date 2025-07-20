from contextlib import asynccontextmanager
import os
from fastapi import FastAPI
from langchain_google_vertexai import VertexAIEmbeddings
from datastore.providers import cloudsql_postgres
from .routes import routes

EMBEDDING_MODEL_NAME = "gemini-embedding-001"

@asynccontextmanager
async def initialize_datastore(app: FastAPI):
    config = cloudsql_postgres.Config(
        kind="cloudsql-postgres",
        project=os.environ.get("DB_PROJECT"),
        region=os.environ.get("DB_REGION"),
        instance=os.environ.get("DB_INSTANCE"),
        user=os.environ.get("DB_USER"),
        password=os.environ.get("DB_PASSWORD"),
        database=os.environ.get("DB_NAME"),
    )
    app.state.datastore = await cloudsql_postgres.Client.create(config)
    app.state.embed_service = VertexAIEmbeddings(model_name=EMBEDDING_MODEL_NAME)
    yield
    await app.state.datastore.close()

app = FastAPI(lifespan=initialize_datastore)
app.include_router(routes)