from app.graph.state import GraphState
from app.core.llm import get_llm
from app.retrieval.metadata_filter import create_chroma_filter
from app.auth.agent_auth import sign_payload
from app.core.constants import SENDER_ROUTER
import json
from langsmith import traceable


@traceable
def metadata_router_node(state: GraphState) -> GraphState:
    """
    Extracts metadata from the question to filter retrieval.
    """
    question = state.get("rewritten_question", state["question"])
    llm = get_llm(temperature=0.0)

    prompt = f"""
    Analyze the following technical question and extract metadata.
    Return ONLY a JSON object with:
    - framework: (e.g. fastapi, pydantic, langchain, django) or null if not specific.
    - query_type: (e.g. how_to, explanation, api_reference, conceptual)

    Question: {question}
    """

    try:
        response = llm.invoke(prompt)
        text = response.content.strip()
        if text.startswith("```json"):
            text = text[7:-3]
        elif text.startswith("```"):
            text = text[3:-3]
        data = json.loads(text)
    except Exception:
        data = {}

    filters = create_chroma_filter(data)

    return {
        **state,
        "metadata_filters": filters,
        "sender_metadata": {
            "sender": SENDER_ROUTER,
            "signature": sign_payload(SENDER_ROUTER, {"action": "routed"}),
        },
    }
