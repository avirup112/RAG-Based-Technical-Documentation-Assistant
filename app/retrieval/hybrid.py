from typing import List, Dict, Any
from app.retrieval.vector_search import dense_search
from app.retrieval.bm25 import sparse_search
from app.retrieval.rrf import reciprocal_rank_fusion

def hybrid_search(query: str, filters: Dict[str, Any] = None) -> List[Dict[str, Any]]:
    """
    Performs hybrid search by combining dense and sparse search with RRF.
    """
    dense_results = dense_search(query, filters)
    sparse_results = sparse_search(query, filters)
    
    fused_results = reciprocal_rank_fusion(dense_results, sparse_results)
    
    return fused_results
