from app.graph.state import GraphState
from sentence_transformers import CrossEncoder
from app.core.config import settings
from app.core.constants import RERANK_K, SENDER_RERANKER
from app.auth.agent_auth import sign_payload
from functools import lru_cache
from langsmith import traceable


@lru_cache()
def get_reranker():
    return CrossEncoder(settings.RERANKER_MODEL, max_length=512, device="cpu")


@traceable
def reranker_node(state: GraphState) -> GraphState:
    """
    Reranks the retrieved documents using a cross-encoder model.
    """
    question = state.get("rewritten_question", state["question"])
    documents = state.get("documents", [])

    if not documents:
        return {
            **state,
            "reranked_docs": [],
            "sender_metadata": {
                "sender": SENDER_RERANKER,
                "signature": sign_payload(SENDER_RERANKER, {"docs_count": 0}),
            },
        }

    reranker = get_reranker()

    # Prepare pairs
    # Limit to top 20 for reranking performance
    docs_to_rerank = documents[:20]
    pairs = [[question, doc["content"]] for doc in docs_to_rerank]

    scores = reranker.predict(pairs)

    for i, doc in enumerate(docs_to_rerank):
        doc["rerank_score"] = float(scores[i])

    # Sort and take top K
    reranked = sorted(docs_to_rerank, key=lambda x: x["rerank_score"], reverse=True)[
        :RERANK_K
    ]

    return {
        **state,
        "reranked_docs": reranked,
        "sender_metadata": {
            "sender": SENDER_RERANKER,
            "signature": sign_payload(SENDER_RERANKER, {"docs_count": len(reranked)}),
        },
    }
