from fastapi import APIRouter, Request
from langchain_core.embeddings import Embeddings
from langchain_google_vertexai import VertexAI
import datastore
from typing import List
from pydantic import BaseModel

class DocumentChunk(BaseModel):
    source_filename: str
    title: str
    authors: str
    publication_date: str
    content: str
    embedding: List[float]

routes = APIRouter()

@routes.get("/")
async def root():
    return {"message": "SARA Retrieval Service is running"}

@routes.get("/documents/search")
async def documents_search(request: Request, query: str, top_k: int = 3):
    ds: datastore.Client = request.app.state.datastore
    embed_service: Embeddings = request.app.state.embed_service
    
    query_embedding = embed_service.embed_query(query)
    search_results = await ds.search_documents(query_embedding, top_k)

    if not search_results:
        return {"answer": "I could not find any relevant information to answer that question."}

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

    llm = VertexAI(model_name="gemini-2.0-flash-001")
    answer = await llm.ainvoke(prompt)

    return {"answer": answer}


@routes.post("/documents/load")
async def load_documents(request: Request, chunks: List[DocumentChunk]):
    ds: datastore.Client = request.app.state.datastore
    dict_chunks = [chunk.model_dump() for chunk in chunks]
    await ds.initialize_data(paper_chunks=dict_chunks)
    return {"status": "ok", "message": f"Database initialized with {len(chunks)} document chunks."}