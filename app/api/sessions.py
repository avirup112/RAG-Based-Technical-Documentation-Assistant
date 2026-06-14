from fastapi import APIRouter
from app.memory.memory import MemoryManager

router = APIRouter()
memory = MemoryManager()


@router.get("/")
async def list_sessions():
    """
    Returns a list of all past sessions (id + title derived from first user message).
    """
    return {"sessions": memory.list_sessions()}


@router.get("/{session_id}/history")
async def get_session_history(session_id: str):
    """
    Returns the full chat history for a given session so the frontend can restore it.
    """
    history = memory.get_history(session_id)
    return {"session_id": session_id, "history": history}
