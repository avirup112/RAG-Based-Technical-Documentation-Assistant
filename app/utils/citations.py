from typing import List, Dict, Any
from app.models.schemas import Citation


def extract_citations(documents: List[Dict[str, Any]]) -> List[Citation]:
    """
    Extracts citations from a list of documents.
    """
    citations = []
    if not documents:
        return citations

    for doc in documents:
        meta = doc.get("metadata", {})
        citations.append(
            Citation(
                source=meta.get("source", "unknown"),
                chunk_id=meta.get("chunk_id", "unknown"),
                content_snippet=doc.get("content", "")[:150] + "...",
            )
        )
    return citations
