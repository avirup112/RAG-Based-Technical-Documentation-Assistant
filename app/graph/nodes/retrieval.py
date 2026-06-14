
from app.graph.state import GraphState
from app.retrieval.hybrid import hybrid_search
from app.retrieval.rrf import reciprocal_rank_fusion
from app.auth.agent_auth import sign_payload
from app.core.constants import SENDER_RETRIEVER
from loguru import logger
from langsmith import traceable

@traceable
def retrieval_node(state: GraphState) -> GraphState:
    """
    Performs hybrid retrieval across ALL expanded queries from the Query Transformation pipeline.
    
    Strategy:
    - For each expanded query (originals + expansions + decomposed sub-questions),
      run a full hybrid search (ChromaDB dense + BM25 sparse).
    - Merge all result sets using Reciprocal Rank Fusion (RRF) to produce a final
      deduplicated, ranked list of documents.
    - This dramatically improves recall since each variant may surface different documents.
    """
    filters = state.get("metadata_filters", None)
    retries = state.get("retries", 0)

    # Prefer expanded_queries if available (from Query Transformation pipeline)
    # Fall back to rewritten_question → original question
    expanded_queries = state.get("expanded_queries")
    if expanded_queries:
        search_queries = expanded_queries
    else:
        search_queries = [state.get("rewritten_question", state["question"])]

    logger.info(f"Retrieval: running hybrid search across {len(search_queries)} query variants.")

    # Run hybrid search for each query variant and collect all result lists
    all_result_sets = []
    for query in search_queries:
        results = hybrid_search(query, filters)
        if results:
            all_result_sets.append(results)
            logger.debug(f"  Query '{query[:60]}...' → {len(results)} docs")

    # Fuse all result sets together using RRF for a single ranked list
    if len(all_result_sets) == 0:
        documents = []
    elif len(all_result_sets) == 1:
        documents = all_result_sets[0]
    else:
        # Progressively fuse: merge first two, then continue folding
        fused = reciprocal_rank_fusion(all_result_sets[0], all_result_sets[1])
        for additional in all_result_sets[2:]:
            fused = reciprocal_rank_fusion(fused, additional)
        documents = fused

    logger.info(f"Retrieval complete: {len(documents)} unique docs after fusion.")

    return {
        **state,
        "documents": documents,
        "retries": retries,
        "sender_metadata": {
            "sender": SENDER_RETRIEVER,
            "signature": sign_payload(SENDER_RETRIEVER, {
                "docs_count": len(documents),
                "query_variants": len(search_queries)
            })
        }
    }
