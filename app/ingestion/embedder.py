from typing import List, Dict, Any
from app.core.embeddings import get_embeddings
import uuid

def prepare_for_embedding(chunks: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """
    Computes embeddings and assigns UUIDs to each chunk.
    """
    embedder = get_embeddings()
    contents = [chunk['content'] for chunk in chunks]
    
    # Compute embeddings in batch
    embeddings = embedder.embed_documents(contents)
    
    for i, chunk in enumerate(chunks):
        chunk['embedding'] = embeddings[i]
        chunk['chunk_id'] = str(uuid.uuid4())
        
    return chunks
