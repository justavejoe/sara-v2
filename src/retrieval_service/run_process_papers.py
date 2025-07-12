# Copyright 2024 Google LLC
# (license header)

import os
import fitz  # PyMuPDF
import pandas as pd
from langchain_google_vertexai import VertexAIEmbeddings
from langchain_text_splitters import RecursiveCharacterTextSplitter

# This should point to your new folder
PDF_DIRECTORY = "./data/papers_to_process/"
OUTPUT_CSV_PATH = "./data/processed_papers.csv"
EMBEDDING_MODEL_NAME = "text-embedding-004"


def process_papers():
    """
    Processes all PDF files in a directory, chunks their text,
    and generates embeddings.
    """
    print("Starting research paper processing...")
    all_chunks = []
    
    # 1. Initialize services
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=1000,
        chunk_overlap=100,
    )
    embed_service = VertexAIEmbeddings(model_name=EMBEDDING_MODEL_NAME)

    # 2. Loop through all PDF files in the directory
    for filename in os.listdir(PDF_DIRECTORY):
        if filename.endswith(".pdf"):
            paper_id = filename.replace(".pdf", "")
            print(f"Processing: {filename}")
            
            # 3. Extract full text from PDF
            doc = fitz.open(os.path.join(PDF_DIRECTORY, filename))
            full_text = "".join(page.get_text() for page in doc)
            
            # 4. Split text into chunks
            chunks = text_splitter.split_text(full_text)
            
            # 5. Create a record for each chunk with paper metadata
            for i, chunk_text in enumerate(chunks):
                all_chunks.append({
                    "paper_id": paper_id,
                    "chunk_id": i,
                    "content": chunk_text
                })

    print(f"Created {len(all_chunks)} text chunks from all papers.")
    
    # 6. Generate embeddings for all chunks in batches
    print("Generating embeddings...")
    contents = [x["content"] for x in all_chunks]
    
    batch_size = 5 # As used in the reference app
    for i in range(0, len(contents), batch_size):
        batch_contents = contents[i : i + batch_size]
        embeddings = embed_service.embed_documents(batch_contents)
        # Add embeddings to our list of chunks
        for j, embedding in enumerate(embeddings):
            all_chunks[i+j]["embedding"] = embedding

    # 7. Save to a CSV file
    df = pd.DataFrame(all_chunks)
    df.to_csv(OUTPUT_CSV_PATH, index=False)
    print(f"Successfully processed papers and saved to {OUTPUT_CSV_PATH}")

if __name__ == "__main__":
    process_papers()