from typing import List, Dict, Any


def reciprocal_rank_fusion(
    dense_results: List[Dict[str, Any]],
    sparse_results: List[Dict[str, Any]],
    k: int = 60,
) -> List[Dict[str, Any]]:
    """
    Fuses results from dense and sparse search using Reciprocal Rank Fusion (RRF).
    """
    rrf_scores = {}
    doc_lookup = {}

    def process_results(results, weight=1.0):
        for rank, doc in enumerate(results):
            chunk_id = doc["metadata"].get("chunk_id")
            if not chunk_id:
                # Fallback to content hash if chunk_id is missing
                chunk_id = str(hash(doc["content"]))

            if chunk_id not in rrf_scores:
                rrf_scores[chunk_id] = 0.0
                doc_lookup[chunk_id] = doc

            # RRF formula: 1 / (k + rank)
            rrf_scores[chunk_id] += weight * (1.0 / (k + rank + 1))

    # Process both result sets
    process_results(dense_results)
    process_results(sparse_results)

    # Sort by fused score
    sorted_chunks = sorted(rrf_scores.items(), key=lambda x: x[1], reverse=True)

    fused_results = []
    for chunk_id, score in sorted_chunks:
        doc = doc_lookup[chunk_id].copy()
        doc["rrf_score"] = score
        fused_results.append(doc)

    return fused_results
