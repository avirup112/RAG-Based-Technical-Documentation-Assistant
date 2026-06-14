import chromadb
from app.core.config import settings
from app.core.constants import COLLECTION_NAME


def get_chroma_client() -> chromadb.ClientAPI:
    """
    Returns a persistent ChromaDB client instance.
    """
    return chromadb.PersistentClient(path=settings.CHROMA_DB_DIR)


def get_collection():
    """
    Returns the main documentation collection.
    """
    client = get_chroma_client()
    return client.get_or_create_collection(
        name=COLLECTION_NAME, metadata={"hnsw:space": "cosine"}
    )
