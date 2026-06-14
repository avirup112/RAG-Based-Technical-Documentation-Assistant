from app.graph.state import GraphState
from app.core.llm import get_llm
from app.auth.agent_auth import sign_payload
from app.core.constants import SENDER_REWRITER
from loguru import logger
from langsmith import traceable

@traceable
def rewrite_node(state: GraphState) -> GraphState:
    """
    Rewrites the question to improve retrieval if no relevant docs were found.
    Clears the query transformation cache (sub_questions, expanded_queries) so the
    full pipeline re-runs on the improved question during the next cycle.
    """
    question = state["question"]
    llm = get_llm(temperature=0.0)
    
    prompt = f"""
    You are a question re-writer that converts an input question to a better version that is optimized
    for vectorstore retrieval. Look at the input and try to reason about the underlying semantic intent / meaning.
    Add relevant technical terms, synonyms, or rephrase to maximize the chance of finding relevant documentation.
    
    Here is the initial question:
    {question}
    
    Formulate an improved question. Return ONLY the improved question.
    """
    
    response = llm.invoke(prompt)
    rewritten_question = response.content.strip()
    retries = state.get("retries", 0) + 1
    
    logger.info(f"Query rewritten (attempt {retries}): {rewritten_question}")
    
    return {
        **state,
        "rewritten_question": rewritten_question,
        "retries": retries,
        # Clear expansion cache so query_analysis re-runs on the new question
        "sub_questions": [],
        "expanded_queries": [],
        "sender_metadata": {
            "sender": SENDER_REWRITER,
            "signature": sign_payload(SENDER_REWRITER, {"retries": retries})
        }
    }
