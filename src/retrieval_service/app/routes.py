from fastapi import APIRouter, Request
from langchain_core.embeddings import Embeddings
import datastore
from typing import List
from pydantic import BaseModel

class DocumentChunk(BaseModel):
    """
    Pydantic model for validating the structure of an incoming document chunk.
    """
    source_filename: str
    title: str
    authors: str
    publication_date: str
    content: str
    embedding: List[float]

routes = APIRouter()

@routes.get("/")
async def root():
    """
    Root endpoint to confirm the service is running.
    """
    return {"message": "SARA Retrieval Service is running"}

@routes.get("/documents/search")
async def documents_search(request: Request, query: str, top_k: int = 3):
    """
    Searches for documents using a query string.
    """
    ds: datastore.Client = request.app.state.datastore
    embed_service: Embeddings = request.app.state.embed_service
    query_embedding = embed_service.embed_query(query)
    results = await ds.search_documents(query_embedding, top_k)
    return {"results": results}


@routes.post("/documents/load")
async def load_documents(request: Request, chunks: List[DocumentChunk]):
    """
    Initializes the database with a list of document chunks.
    The 'chunks' parameter is validated against the DocumentChunk model.
    """
    ds: datastore.Client = request.app.state.datastore
    # Convert the Pydantic models back to dictionaries for the datastore client
    dict_chunks = [chunk.model_dump() for chunk in chunks]
    await ds.initialize_data(paper_chunks=dict_chunks)
    return {"status": "ok", "message": f"Database initialized with {len(chunks)} document chunks."}