from app.graph.state import GraphState
from app.core.llm import get_llm
from app.auth.agent_auth import sign_payload
from app.core.constants import SENDER_GENERATOR
from app.security.output_guard import check_output_safety
from loguru import logger
from langsmith import traceable

# Prompt templates tailored to each query type
QUERY_TYPE_INSTRUCTIONS = {
    "how_to": (
        "Provide a clear, step-by-step answer. "
        "Use numbered steps and include code examples where applicable."
    ),
    "conceptual": (
        "Explain the concept clearly and concisely. "
        "Use analogies or diagrams in markdown if helpful. "
        "Avoid unnecessary implementation details unless asked."
    ),
    "api_reference": (
        "Focus on the exact API, its parameters, return values, and usage. "
        "Always include a code snippet showing the API in action."
    ),
    "troubleshooting": (
        "Identify the likely root cause first, then provide a solution. "
        "List common pitfalls and how to avoid them."
    ),
}


@traceable
def generation_node(state: GraphState) -> GraphState:
    """
    Generates an answer based on the relevant documents.
    Uses query_type from the Query Transformation pipeline to tailor
    the response style (how-to, conceptual, api_reference, troubleshooting).
    """
    question = state["question"]
    docs = state.get("relevant_docs", [])
    query_type = state.get("query_type", "conceptual")
    sub_questions = state.get("sub_questions", [])

    if not docs:
        return {
            **state,
            "answer": "I could not find any relevant documentation to answer your question.",
            "sender_metadata": {
                "sender": SENDER_GENERATOR,
                "signature": sign_payload(SENDER_GENERATOR, {"status": "no_docs"}),
            },
        }

    # Build context from retrieved docs
    context = "\n\n".join(
        [
            f"Source: {d['metadata'].get('source', 'Unknown')}\nContent:\n{d['content']}"
            for d in docs
        ]
    )

    llm = get_llm(temperature=0.0)

    # Build conversation history string (it is already bounded/summarized by MemoryManager)
    chat_history = state.get("chat_history", [])
    history_str = "\n".join(
        [f"{msg['role']}: {msg['content']}" for msg in chat_history]
    )

    # Get style instruction for this query type
    style_instruction = QUERY_TYPE_INSTRUCTIONS.get(
        query_type, QUERY_TYPE_INSTRUCTIONS["conceptual"]
    )

    # If the question was decomposed, remind the LLM to address all sub-questions
    # but NOT to format them as separate headings or sections — answer must be unified prose.
    sub_q_section = ""
    if len(sub_questions) > 1:
        sub_q_list = ", ".join([f'"{q}"' for q in sub_questions])
        sub_q_section = (
            f"\nThe user's question was internally decomposed into these aspects: {sub_q_list}. "
            "Address all of them in a single, unified, coherent answer. "
            "Do NOT use the sub-questions as headings or list items in your response.\n"
        )

    prompt = f"""You are an expert technical documentation assistant.
Use ONLY the retrieved context below to answer the question. Do not make up information.
If you don't know, say "I don't know based on the available documentation."
Write your answer as clear, unified prose. Do not echo back the question or list sub-questions as headings.

Response style ({query_type}): {style_instruction}
{sub_q_section}
Conversation History:
{history_str}

Question: {question}

Retrieved Context:
{context}

Answer:
"""

    logger.info(f"Generating answer for query_type='{query_type}'")
    response = llm.invoke(prompt)
    answer = response.content.strip()

    # Output guard check
    is_safe = check_output_safety(answer)
    if not is_safe:
        answer = "I'm sorry, but I cannot provide that information due to safety constraints."
        logger.warning("Output guard blocked the generated answer.")

    return {
        **state,
        "answer": answer,
        "sender_metadata": {
            "sender": SENDER_GENERATOR,
            "signature": sign_payload(
                SENDER_GENERATOR,
                {"status": "generated", "is_safe": is_safe, "query_type": query_type},
            ),
        },
    }
