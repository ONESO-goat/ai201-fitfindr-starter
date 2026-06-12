import os
from dotenv import load_dotenv

load_dotenv()

# --- LLM ---
class Config:
    GROQ_API_KEY = os.getenv("GROQ_API_KEY")
    LLM_MODEL = "llama-3.3-70b-versatile"


    # --- Embeddings ---
    EMBEDDING_MODEL = "all-MiniLM-L6-v2"

    # --- Vector store ---
    CHROMA_COLLECTION = "fitfinder"
    CHROMA_PATH = "./chroma_db"

    # --- Retrieval ---
    N_RESULTS = 3

if not Config.GROQ_API_KEY:
    raise RuntimeError("GROQ_API_KEY environment variable not found")

if __name__ == "__main__":
    print(Config.N_RESULTS)