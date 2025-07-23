from contextlib import asynccontextmanager
import os
from fastapi import FastAPI
# The VertexAIEmbeddings import is no longer needed here
from datastore.providers import cloudsql_postgres
from .routes import routes

@asynccontextmanager
async def initialize_datastore(app: FastAPI):
    """
    Initializes the database connection at startup.
    """
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
    
    # The embedding service is no longer created here to prevent startup errors.
    
    yield
    
    # Clean up the datastore connection when the app shuts down.
    if getattr(app.state, "datastore", None):
        await app.state.datastore.close()

app = FastAPI(lifespan=initialize_datastore)

# We'll use app.state to hold the embedding service, initializing it as None.
app.state.embed_service = None 
app.include_router(routes)