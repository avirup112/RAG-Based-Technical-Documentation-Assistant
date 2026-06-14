from app.graph.state import GraphState
from app.retrieval.web_search import search_web
from app.auth.agent_auth import sign_payload
from langsmith import traceable

@traceable
def web_search_node(state: GraphState) -> GraphState:
    """
    Performs web search as a fallback if internal retrieval fails after max retries.
    """
    question = state.get("rewritten_question", state["question"])
    
    web_docs = search_web(question)
    
    relevant_docs = state.get("relevant_docs", [])
    relevant_docs.extend(web_docs)
    
    return {
        **state,
        "relevant_docs": relevant_docs,
        "sender_metadata": {
            "sender": "web_search",
            "signature": sign_payload("web_search", {"docs_count": len(web_docs)})
        }
    }
