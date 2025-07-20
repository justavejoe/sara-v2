from fastapi import APIRouter, Request
from langchain_core.embeddings import Embeddings
from langchain_google_vertexai import VertexAI
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
    Searches for documents and generates a natural language answer using RAG.
    """
    ds: datastore.Client = request.app.state.datastore
    embed_service: Embeddings = request.app.state.embed_service

    # 1. RETRIEVE relevant document chunks
    query_embedding = embed_service.embed_query(query)
    search_results = await ds.search_documents(query_embedding, top_k)

    if not search_results:
        return {"answer": "I could not find any relevant information to answer that question."}

    # 2. AUGMENT the context for the generative model
    context = "\n---\n".join([result['content'] for result in search_results])
    
    prompt = f"""
    Use only the context below to answer the user's question.
    If the answer is not available in the context, say "I could not find an answer in the provided documents."

    CONTEXT:
    {context}
    
    QUESTION:
    {query}

    ANSWER:
    """

    # 3. GENERATE an answer
    llm = VertexAI(model_name="gemini-1.5-flash") # Using a fast and capable model
    answer = await llm.ainvoke(prompt)

    # Return the generated answer instead of the raw search results
    return {"answer": answer}


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