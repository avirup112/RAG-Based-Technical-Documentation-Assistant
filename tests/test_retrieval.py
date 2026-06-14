
from app.retrieval.rrf import reciprocal_rank_fusion

def test_rrf():
    dense = [{"content": "A", "metadata": {"chunk_id": "1"}, "score": 0.9}]
    sparse = [{"content": "B", "metadata": {"chunk_id": "2"}, "score": 10.0}]
    
    fused = reciprocal_rank_fusion(dense, sparse, k=60)
    assert len(fused) == 2
    
    # Both are rank 0 in their respective lists, so their RRF scores should be identical (1/61)
    # However, since they are different items, order depends on which was processed first
    assert "rrf_score" in fused[0]
