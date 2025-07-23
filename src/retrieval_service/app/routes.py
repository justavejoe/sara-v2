import os
import fitz  # PyMuPDF
import re
from fastapi import APIRouter, Request, UploadFile, File
from langchain_core.embeddings import Embeddings
from langchain_google_vertexai import VertexAI, VertexAIEmbeddings # Add VertexAIEmbeddings
from langchain_text_splitters import RecursiveCharacterTextSplitter
import datastore
from typing import List
from pydantic import BaseModel

# --- Pydantic Model (no changes) ---
class DocumentChunk(BaseModel):
    source_filename: str
    title: str
    authors: str
    publication_date: str
    content: str
    embedding: List[float]

routes = APIRouter()
EMBEDDING_MODEL_NAME = "text-embedding-004"

# --- New Helper Function ---
def get_embed_service(request: Request) -> Embeddings:
    """
    Lazily initializes and returns the embedding service.
    This function creates the service on the first request, which avoids
    startup race conditions with IAM permissions.
    """
    if not getattr(request.app.state, "embed_service", None):
        print("Initializing embedding service for the first time...")
        request.app.state.embed_service = VertexAIEmbeddings(
            model_name=EMBEDDING_MODEL_NAME,
            project=os.environ.get("DB_PROJECT"),
            location=os.environ.get("DB_REGION"),
        )
    return request.app.state.embed_service

# --- Helper Functions for Processing (no changes) ---
def classify_document(first_page_text: str) -> str:
    patent_keywords = ["united states patent", "patent no.", "(72) inventors", "(73) assignee"]
    if any(keyword in first_page_text.lower() for keyword in patent_keywords):
        return "patent"
    return "paper"

def extract_patent_metadata(first_page_text: str) -> dict:
    patterns = {
        'title': re.compile(r'\(54\)\s(.*?)\(71\)', re.DOTALL),
        'inventors': re.compile(r'\(72\)\sInventors?:\s*(.*?)(?=\n\(|$)'),
        'assignee': re.compile(r'\(73\)\sAssignee:\s*(.*?)(?=\n\(|$)'),
        'publication_date': re.compile(r'\(45\)\sDate of Patent:\s*(.*?)(?=\n\(|$)'),
    }
    metadata = {}
    for key, pattern in patterns.items():
        match = pattern.search(first_page_text)
        metadata[key] = match.group(1).replace('\n', ' ').strip() if match else 'Not Found'
    return metadata

def extract_paper_metadata(doc_metadata: dict, filename: str) -> dict:
    return {
        'title': doc_metadata.get('title', filename),
        'authors': doc_metadata.get('author', 'Unknown Authors'),
        'publication_date': doc_metadata.get('creationDate', 'Unknown Date')
    }

# --- API Routes ---
@routes.get("/")
async def root():
    return {"message": "SARA Retrieval Service is running"}

@routes.post("/documents/upload")
async def upload_documents(request: Request, files: List[UploadFile] = File(...)):
    ds: datastore.Client = request.app.state.datastore
    embed_service = get_embed_service(request) # Use the helper
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=100)
    all_chunks, processed_files = [], []

    for file in files:
        try:
            file_content = await file.read()
            doc = fitz.open(stream=file_content, filetype="pdf")
            first_page_text = doc[0].get_text("text", sort=True)
            doc_type = classify_document(first_page_text)
            if doc_type == "patent":
                metadata = extract_patent_metadata(first_page_text)
                title = metadata.get('title', file.filename)
                authors = f"Inventors: {metadata.get('inventors', 'N/A')}; Assignee: {metadata.get('assignee', 'N/A')}"
                publication_date = metadata.get('publication_date', 'N/A')
            else:
                metadata = extract_paper_metadata(doc.metadata, file.filename)
                title, authors, publication_date = metadata.get('title'), metadata.get('authors'), metadata.get('publication_date')
            full_text = " ".join([page.get_text() for page in doc])
            doc.close()
            chunks = text_splitter.split_text(full_text)
            for chunk_text in chunks:
                all_chunks.append({"source_filename": file.filename, "title": title, "authors": authors, "publication_date": publication_date, "content": chunk_text})
            processed_files.append(file.filename)
        except Exception as e:
            return {"status": "error", "message": f"Failed to process {file.filename}: {str(e)}"}

    if not all_chunks:
        return {"status": "error", "message": "No text could be extracted."}

    contents = [chunk["content"] for chunk in all_chunks]
    for i in range(0, len(contents), 5):
        batch_contents = contents[i:i + 5]
        embeddings = embed_service.embed_documents(batch_contents)
        for j, embedding in enumerate(embeddings):
            all_chunks[i + j]["embedding"] = embedding
    
    await ds.add_documents(all_chunks)
    return {"status": "ok", "message": f"Successfully processed {len(processed_files)} files.", "files": processed_files}

@routes.get("/documents/search")
async def documents_search(request: Request, query: str, top_k: int = 3):
    ds: datastore.Client = request.app.state.datastore
    embed_service = get_embed_service(request) # Use the helper
    query_embedding = embed_service.embed_query(query)
    search_results = await ds.search_documents(query_embedding, top_k)
    if not search_results:
        return {"answer": "I could not find any relevant information."}
    context = "\n---\n".join([result['content'] for result in search_results])
    prompt = f"Use only the context below to answer the user's question.\nCONTEXT:\n{context}\n\nQUESTION:\n{query}\n\nANSWER:"
    llm = VertexAI(model_name="gemini-1.5-flash-001")
    answer = await llm.ainvoke(prompt)
    return {"answer": answer}

@routes.post("/documents/load")
async def load_documents(request: Request, chunks: List[DocumentChunk]):
    ds: datastore.Client = request.app.state.datastore
    dict_chunks = [chunk.model_dump() for chunk in chunks]
    await ds.initialize_data(paper_chunks=dict_chunks)
    return {"status": "ok", "message": f"Database initialized with {len(chunks)} document chunks."}