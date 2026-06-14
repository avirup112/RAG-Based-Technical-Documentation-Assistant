from dotenv import load_dotenv
import os

load_dotenv()


class Settings:
    GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")

    CHROMA_DB_PATH = os.getenv("CHROMA_DB_PATH", "./chroma_db")

    EMBEDDING_MODEL = os.getenv(
        "EMBEDDING_MODEL", "sentence-transformers/all-MiniLM-L6-v2"
    )
