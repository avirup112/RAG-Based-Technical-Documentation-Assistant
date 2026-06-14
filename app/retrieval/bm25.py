from rank_bm25 import BM25Okapi
from app.vectordb.chroma_client import get_collection
from app.core.constants import BM25_K
from typing import List, Dict, Any


def build_bm25_index(filters: Dict[str, Any] = None) -> tuple[BM25Okapi, List[Dict]]:
    """
    Fetches documents from ChromaDB and builds a BM25 index on the fly.
    In a high-scale production system, this should be pre-computed and stored.
    """
    collection = get_collection()
    results = collection.get(where=filters, include=['documents', 'metadatas'])
    
    documents = results.get('documents', [])
    metadatas = results.get('metadatas', [])
    
    if not documents:
        return None, []
        
    tokenized_corpus = [doc.lower().split() for doc in documents]
    bm25 = BM25Okapi(tokenized_corpus)
    
    corpus_data = [
        {"content": doc, "metadata": meta}
        for doc, meta in zip(documents, metadatas)
    ]
    return bm25, corpus_data

def sparse_search(query: str, filters: Dict[str, Any] = None, k: int = BM25_K) -> List[Dict[str, Any]]:
    """
    Performs sparse search using BM25.
    """
    bm25, corpus_data = build_bm25_index(filters)
    if not bm25:
        return []
        
    tokenized_query = query.lower().split()
    doc_scores = bm25.get_scores(tokenized_query)
    
    # Get top K indices
    top_n = sorted(range(len(doc_scores)), key=lambda i: doc_scores[i], reverse=True)[:k]
    
    docs = []
    for idx in top_n:
        if doc_scores[idx] > 0:
            docs.append({
                "content": corpus_data[idx]["content"],
                "metadata": corpus_data[idx]["metadata"],
                "score": doc_scores[idx]
            })
    return docs
