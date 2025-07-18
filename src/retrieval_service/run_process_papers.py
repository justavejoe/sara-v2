# Copyright 2024 Google LLC
# (license header)

import os
from pypdf import PdfReader # Use the new library
import pandas as pd
from langchain_google_vertexai import VertexAIEmbeddings
from langchain_text_splitters import RecursiveCharacterTextSplitter

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

    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=1000,
        chunk_overlap=100,
    )
    embed_service = VertexAIEmbeddings(model_name=EMBEDDING_MODEL_NAME)

    for filename in os.listdir(PDF_DIRECTORY):
        if filename.endswith(".pdf"):
            paper_id = filename.replace(".pdf", "")
            print(f"Processing: {filename}")

            # Use PdfReader to extract text
            reader = PdfReader(os.path.join(PDF_DIRECTORY, filename))
            full_text = ""
            for page in reader.pages:
                full_text += page.extract_text()

            chunks = text_splitter.split_text(full_text)

            for i, chunk_text in enumerate(chunks):
                all_chunks.append({
                    "paper_id": paper_id,
                    "chunk_id": i,
                    "content": chunk_text
                })

    print(f"Created {len(all_chunks)} text chunks from all papers.")

    print("Generating embeddings...")
    contents = [x["content"] for x in all_chunks]

    batch_size = 5
    for i in range(0, len(contents), batch_size):
        batch_contents = contents[i : i + batch_size]
        embeddings = embed_service.embed_documents(batch_contents)
        for j, embedding in enumerate(embeddings):
            all_chunks[i+j]["embedding"] = embedding

    df = pd.DataFrame(all_chunks)
    df.to_csv(OUTPUT_CSV_PATH, index=False)
    print(f"Successfully processed papers and saved to {OUTPUT_CSV_PATH}")

if __name__ == "__main__":
    process_papers()