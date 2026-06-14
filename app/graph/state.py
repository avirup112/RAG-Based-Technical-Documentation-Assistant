from typing import List, Dict, Any, TypedDict
from typing_extensions import NotRequired

class GraphState(TypedDict):
    """
    Represents the state of our graph.
    """
    question: str
    rewritten_question: NotRequired[str]
    sub_questions: NotRequired[List[str]]        # Query Decomposition results
    expanded_queries: NotRequired[List[str]]     # Query Expansion results
    query_type: NotRequired[str]                 # e.g., how_to, conceptual, api_reference
    documents: NotRequired[List[Dict[str, Any]]]
    reranked_docs: NotRequired[List[Dict[str, Any]]]
    relevant_docs: NotRequired[List[Dict[str, Any]]]
    answer: NotRequired[str]
    retries: NotRequired[int]
    hallucination_score: NotRequired[str]
    metadata_filters: NotRequired[Dict[str, Any]]
    sender_metadata: NotRequired[Dict[str, str]]
    error: NotRequired[str]
    session_id: NotRequired[str]
    chat_history: NotRequired[List[Dict[str, str]]]
