from app.graph.state import GraphState
from app.memory.memory import MemoryManager
from langsmith import traceable


@traceable
def memory_saver_node(state: GraphState) -> GraphState:
    """
    Saves the final answer into the conversation memory.
    """
    session_id = state.get("session_id")
    question = state.get("question")
    answer = state.get("answer")

    if session_id and question and answer:
        manager = MemoryManager()
        manager.save_interaction(session_id, question, answer)

    return state
