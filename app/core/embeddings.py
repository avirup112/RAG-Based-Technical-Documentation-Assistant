from langchain_community.embeddings import HuggingFaceEmbeddings
from app.core.config import settings
from functools import lru_cache

@lru_cache()
def get_embeddings() -> HuggingFaceEmbeddings:
    """
    Returns a cached instance of the HuggingFace embeddings model.
    """
    return HuggingFaceEmbeddings(
        model_name=settings.EMBEDDING_MODEL,
        model_kwargs={'device': 'cpu'}, # Use 'cuda' if available
        encode_kwargs={'normalize_embeddings': True}
    )
