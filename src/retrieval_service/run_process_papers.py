import os
import fitz  # PyMuPDF library
import pandas as pd
from langchain_google_vertexai import VertexAIEmbeddings
from langchain_text_splitters import RecursiveCharacterTextSplitter

PDF_DIRECTORY = "./data/papers_to_process/"
OUTPUT_CSV_PATH = "./data/processed_papers.csv"
EMBEDDING_MODEL_NAME = "text-embedding-004"

def process_papers():
    """
    Processes all PDF files, extracts metadata, chunks text, and generates embeddings.
    """
    print("Starting research paper processing...")
    all_chunks = []

    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=1000,
        chunk_overlap=100,
    )
    
    # Initialize the embedding service, specifying the project
    embed_service = VertexAIEmbeddings(
        model_name=EMBEDDING_MODEL_NAME,
        project=os.environ.get("GOOGLE_CLOUD_PROJECT"),
    )

    for filename in os.listdir(PDF_DIRECTORY):
        if filename.endswith(".pdf"):
            print(f"Processing: {filename}")
            try:
                doc = fitz.open(os.path.join(PDF_DIRECTORY, filename))
                metadata = doc.metadata
                title = metadata.get('title', filename.replace(".pdf", ""))
                authors = metadata.get('author', 'Unknown Authors')
                publication_date = metadata.get('creationDate', 'Unknown Date') 
                
                full_text = " ".join([page.get_text() for page in doc])
                doc.close()
            except Exception as e:
                print(f"Could not process {filename}. Error: {e}")
                continue

            chunks = text_splitter.split_text(full_text)

            for chunk_text in chunks:
                all_chunks.append({
                    "source_filename": filename,
                    "title": title,
                    "authors": authors,
                    "publication_date": publication_date,
                    "content": chunk_text
                })

    if not all_chunks:
        print("No chunks were created. Exiting.")
        return

    print(f"Created {len(all_chunks)} text chunks from all papers.")
    print("Generating embeddings...")
    contents = [x["content"] for x in all_chunks]

    batch_size = 5 
    for i in range(0, len(contents), batch_size):
        batch_contents = contents[i : i + batch_size]
        try:
            embeddings = embed_service.embed_documents(batch_contents)
            for j, embedding in enumerate(embeddings):
                all_chunks[i+j]["embedding"] = embedding
        except Exception as e:
            print(f"Error embedding batch starting at index {i}. Error: {e}")
            for j in range(len(batch_contents)):
                 all_chunks[i+j]["embedding"] = None

    df = pd.DataFrame(all_chunks)
    df.dropna(subset=['embedding'], inplace=True)
    df.to_csv(OUTPUT_CSV_PATH, index=False)
    print(f"Successfully processed papers and saved to {OUTPUT_CSV_PATH}")

if __name__ == "__main__":
    process_papers()