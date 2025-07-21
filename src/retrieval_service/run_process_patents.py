import os
import fitz  # PyMuPDF
import pandas as pd
import re
from langchain_google_vertexai import VertexAIEmbeddings
from langchain_text_splitters import RecursiveCharacterTextSplitter

# Define input/output paths
PATENT_DIRECTORY = "./data/patents_to_process/"
OUTPUT_CSV_PATH = "./data/processed_patents.csv"
EMBEDDING_MODEL_NAME = "text-embedding-004"


def extract_patent_metadata(first_page_text: str):
    """
    Extracts key metadata from the text of the first page of a patent PDF
    using regular expressions.
    """
    # Regex patterns for common US patent formats. These may need refinement.
    patterns = {
        'patent_id': re.compile(r'\(12\)\sUnited States Patent\s.*?\(10\)\sPatent No\.:\s*(US\s[\d,]+)', re.DOTALL),
        'title': re.compile(r'\(54\)\s(.*?)\(71\)', re.DOTALL),
        'inventors': re.compile(r'\(72\)\sInventors:\s*(.*?)(?=\n\(|$)'),
        'assignee': re.compile(r'\(73\)\sAssignee:\s*(.*?)(?=\n\(|$)'),
        'publication_date': re.compile(r'\(45\)\sDate of Patent:\s*(.*?)(?=\n\(|$)'),
    }

    metadata = {}
    for key, pattern in patterns.items():
        match = pattern.search(first_page_text)
        if match:
            # Clean up the extracted text
            metadata[key] = match.group(1).replace('\n', ' ').strip()
        else:
            metadata[key] = 'Not Found'
            
    return metadata


def process_patents():
    """
    Processes all PDF patent files, extracts metadata, chunks text, 
    and generates embeddings.
    """
    print("Starting patent processing...")
    all_chunks = []

    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=1000,
        chunk_overlap=100,
    )
    
    embed_service = VertexAIEmbeddings(
        model_name=EMBEDDING_MODEL_NAME,
        project=os.environ.get("GOOGLE_CLOUD_PROJECT"),
    )

    if not os.path.exists(PATENT_DIRECTORY):
        print(f"Error: Directory not found at '{PATENT_DIRECTORY}'")
        return

    for filename in os.listdir(PATENT_DIRECTORY):
        if filename.lower().endswith(".pdf"):
            print(f"Processing: {filename}")
            try:
                doc = fitz.open(os.path.join(PATENT_DIRECTORY, filename))
                
                # Metadata extraction from the first page
                first_page_text = doc[0].get_text("text", sort=True)
                metadata = extract_patent_metadata(first_page_text)

                # For the database, we'll use the extracted metadata
                # and combine some fields for consistency with the 'document_chunks' table
                title = metadata.get('title', filename.replace(".pdf", ""))
                # Combine inventors and assignee into a single 'authors' field
                authors = f"Inventors: {metadata.get('inventors', 'N/A')}; Assignee: {metadata.get('assignee', 'N/A')}"
                publication_date = metadata.get('publication_date', 'N/A')

                # Extract full text for chunking and embedding
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

    print(f"Created {len(all_chunks)} text chunks from all patents.")
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
    print(f"Successfully processed patents and saved to {OUTPUT_CSV_PATH}")

if __name__ == "__main__":
    process_patents()