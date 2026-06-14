from app.graph.state import GraphState
from app.memory.memory import MemoryManager
from langsmith import traceable


@traceable
def memory_loader_node(state: GraphState) -> GraphState:
    """
    Loads conversation memory into the graph state.
    """
    session_id = state.get("session_id")

    if not session_id:
        return state

    manager = MemoryManager()
    chat_history = manager.get_history(session_id)

    return {**state, "chat_history": chat_history}
