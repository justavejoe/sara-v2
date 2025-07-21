import fitz  # PyMuPDF
import re
from fastapi import APIRouter, Request, UploadFile, File
from langchain_core.embeddings import Embeddings
from langchain_google_vertexai import VertexAI
from langchain_text_splitters import RecursiveCharacterTextSplitter
import datastore
from typing import List
from pydantic import BaseModel

# --- Helper Functions for Processing ---

def classify_document(first_page_text: str) -> str:
    """Classifies a document as 'patent' or 'paper' based on keywords."""
    patent_keywords = ["united states patent", "patent no.", "(72) inventors", "(73) assignee"]
    if any(keyword in first_page_text.lower() for keyword in patent_keywords):
        return "patent"
    return "paper"

def extract_patent_metadata(first_page_text: str) -> dict:
    """Extracts metadata from patent text using regex."""
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
    """Extracts metadata from a research paper's properties."""
    return {
        'title': doc_metadata.get('title', filename),
        'authors': doc_metadata.get('author', 'Unknown Authors'),
        'publication_date': doc_metadata.get('creationDate', 'Unknown Date')
    }

# --- Pydantic Model (no changes) ---

class DocumentChunk(BaseModel):
    source_filename: str
    title: str
    authors: str
    publication_date: str
    content: str
    embedding: List[float]

# --- API Routes ---

routes = APIRouter()

@routes.get("/")
async def root():
    return {"message": "SARA Retrieval Service is running"}

@routes.post("/documents/upload")
async def upload_documents(request: Request, files: List[UploadFile] = File(...)):
    """
    Receives uploaded files, processes them, and adds them to the database.
    """
    ds: datastore.Client = request.app.state.datastore
    embed_service: Embeddings = request.app.state.embed_service
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=100)
    
    all_chunks = []
    processed_files = []

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
            else: # paper
                metadata = extract_paper_metadata(doc.metadata, file.filename)
                title = metadata.get('title')
                authors = metadata.get('authors')
                publication_date = metadata.get('publication_date')

            full_text = " ".join([page.get_text() for page in doc])
            doc.close()

            chunks = text_splitter.split_text(full_text)
            for chunk_text in chunks:
                all_chunks.append({
                    "source_filename": file.filename,
                    "title": title,
                    "authors": authors,
                    "publication_date": publication_date,
                    "content": chunk_text
                })
            processed_files.append(file.filename)
        except Exception as e:
            return {"status": "error", "message": f"Failed to process {file.filename}: {str(e)}"}

    if not all_chunks:
        return {"status": "error", "message": "No text could be extracted from the provided files."}

    # Generate embeddings in batches
    contents = [chunk["content"] for chunk in all_chunks]
    batch_size = 5
    for i in range(0, len(contents), batch_size):
        batch_contents = contents[i:i + batch_size]
        embeddings = embed_service.embed_documents(batch_contents)
        for j, embedding in enumerate(embeddings):
            all_chunks[i + j]["embedding"] = embedding
    
    # Add the processed chunks to the database
    await ds.add_documents(all_chunks)

    return {"status": "ok", "message": f"Successfully processed and added {len(processed_files)} files.", "files": processed_files}


@routes.get("/documents/search")
async def documents_search(request: Request, query: str, top_k: int = 3):
    # ... (this function remains unchanged)
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
    # ... (this function remains unchanged but will now be used for manual overrides)
    ds: datastore.Client = request.app.state.datastore
    dict_chunks = [chunk.model_dump() for chunk in chunks]
    await ds.initialize_data(paper_chunks=dict_chunks)
    return {"status": "ok", "message": f"Database initialized with {len(chunks)} document chunks."}