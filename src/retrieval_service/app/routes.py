# Copyright 2024 Google LLC
# (license header)

from fastapi import APIRouter, Request
from langchain_core.embeddings import Embeddings

import datastore

routes = APIRouter()


@routes.get("/")
async def root():
    """
    Root endpoint for health checks.
    """
    return {"message": "SARA Retrieval Service is running"}


@routes.get("/documents/search")
async def documents_search(query: str, top_k: int = 3, request: Request):
    """
    Searches for documents based on a query.
    """
    ds: datastore.Client = request.app.state.datastore
    embed_service: Embeddings = request.app.state.embed_service

    query_embedding = embed_service.embed_query(query)

    results = await ds.search_documents(query_embedding, top_k)
    return {"results": results}


@routes.get("/data/import")
async def import_data(request: Request):
    """
    Initializes the database with processed paper data.
    """
    ds: datastore.Client = request.app.state.datastore
    await ds.initialize_data()
    return {"status": "ok", "message": "Database initialized with paper chunks."}