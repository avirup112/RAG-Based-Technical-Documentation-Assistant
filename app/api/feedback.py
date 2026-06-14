from fastapi import APIRouter, Depends
from app.models.schemas import FeedbackRequest
from app.auth.jwt_auth import verify_token
from app.memory.memory import MemoryManager
from loguru import logger

router = APIRouter()


@router.post("/")
async def submit_feedback(
    feedback: FeedbackRequest, username: str = Depends(verify_token)
):
    """
    Submits user feedback for an answer. Requires JWT auth.
    """
    logger.info(
        f"Feedback received from {username}: Helpful={feedback.is_helpful}, Comments={feedback.comments}"
    )

    # Store feedback in MongoDB
    manager = MemoryManager()
    manager.save_feedback(
        session_id=feedback.session_id or "unknown_session",
        question=feedback.question,
        answer=feedback.answer,
        is_helpful=feedback.is_helpful,
        comments=feedback.comments,
    )

    return {"status": "Feedback recorded successfully"}
