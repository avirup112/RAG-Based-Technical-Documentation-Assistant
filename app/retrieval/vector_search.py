from app.vectordb.chroma_client import get_collection
from app.core.embeddings import get_embeddings
from app.core.constants import DENSE_K
from typing import List, Dict, Any


def dense_search(
    query: str, filters: Dict[str, Any] = None, k: int = DENSE_K
) -> List[Dict[str, Any]]:
    """
    Performs dense vector search using ChromaDB.
    """
    collection = get_collection()
    embeddings_model = get_embeddings()
    query_embedding = embeddings_model.embed_query(query)

    results = collection.query(
        query_embeddings=[query_embedding],
        n_results=k,
        where=filters,
        include=["documents", "metadatas", "distances"],
    )

    docs = []
    if results["documents"] and len(results["documents"]) > 0:
        for idx, doc in enumerate(results["documents"][0]):
            docs.append(
                {
                    "content": doc,
                    "metadata": results["metadatas"][0][idx],
                    "score": 1.0
                    - results["distances"][0][
                        idx
                    ],  # Convert cosine distance to similarity
                }
            )
    return docs
