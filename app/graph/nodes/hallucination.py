from app.graph.state import GraphState
from app.core.llm import get_judge_llm
from app.auth.agent_auth import sign_payload
from app.core.constants import SENDER_HALLUCINATION
from langsmith import traceable


@traceable
def hallucination_node(state: GraphState) -> GraphState:
    """
    Checks if the generated answer is supported by the retrieved context.
    """
    answer = state.get("answer", "")
    docs = state.get("relevant_docs", [])

    if not docs or not answer:
        return {**state, "hallucination_score": "unknown"}

    llm = get_judge_llm(temperature=0.0)

    context = "\n\n".join(
        [
            f"Source: {d['metadata'].get('source', 'Unknown')}\nContent:\n{d['content']}"
            for d in docs
        ]
    )

    prompt = f"""
    You are a grader assessing whether an answer is grounded in / supported by a set of facts.
    
    Here are the facts:
    {context}
    
    Here is the answer:
    {answer}
    
    Give a binary score 'yes' or 'no' to indicate whether the answer is grounded in / supported by the facts.
    Answer ONLY 'yes' or 'no'.
    """

    response = llm.invoke(prompt)
    score = response.content.strip().lower()

    if "no" in score:
        answer = "I found some documentation, but I could not generate a fully verified answer based strictly on the provided context."

    return {
        **state,
        "answer": answer,
        "hallucination_score": "fail" if "no" in score else "pass",
        "sender_metadata": {
            "sender": SENDER_HALLUCINATION,
            "signature": sign_payload(SENDER_HALLUCINATION, {"score": score}),
        },
    }
