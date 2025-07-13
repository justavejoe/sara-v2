import pandas as pd
import requests
import os
import json

# --- You will need to set these environment variables ---
BACKEND_URL = os.environ.get("BACKEND_URL")
ID_TOKEN = os.environ.get("ID_TOKEN")

CSV_PATH = "./data/processed_papers.csv"

def run_load():
    if not all([BACKEND_URL, ID_TOKEN]):
        print("Error: Please set BACKEND_URL and ID_TOKEN environment variables.")
        return

    print(f"Reading data from {CSV_PATH}...")
    df = pd.read_csv(CSV_PATH)

    # The 'embedding' column is a string, convert it back to a list of floats
    df['embedding'] = df['embedding'].apply(lambda x: json.loads(x))

    chunks = df.to_dict('records')

    headers = {
        "Authorization": f"Bearer {ID_TOKEN}",
        "Content-Type": "application/json"
    }

    print(f"Loading {len(chunks)} chunks to {BACKEND_URL}/documents/load...")
    response = requests.post(f"{BACKEND_URL}/documents/load", json=chunks, headers=headers)

    if response.status_code == 200:
        print("Success!")
        print(response.json())
    else:
        print(f"Error: {response.status_code}")
        print(response.text)

if __name__ == "__main__":
    run_load()