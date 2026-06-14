from app.graph.state import GraphState
from app.security.prompt_injection import check_prompt_injection
from app.auth.agent_auth import sign_payload
from app.core.constants import SENDER_SECURITY
from langsmith import traceable

@traceable
def security_node(state: GraphState) -> GraphState:
    """
    Checks the question for prompt injections.
    """
    question = state["question"]
    is_safe = check_prompt_injection(question)
    
    if not is_safe:
        return {
            **state,
            "error": "Query blocked by security policies.",
            "answer": "I cannot answer this request due to security restrictions.",
            "sender_metadata": {"sender": SENDER_SECURITY, "signature": sign_payload(SENDER_SECURITY, {"action": "blocked"})}
        }
        
    return {
        **state,
        "sender_metadata": {"sender": SENDER_SECURITY, "signature": sign_payload(SENDER_SECURITY, {"action": "allowed"})}
    }
