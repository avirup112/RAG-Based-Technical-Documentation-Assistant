from fastapi import APIRouter, Depends, BackgroundTasks
from app.auth.jwt_auth import verify_token
from app.ingestion.ingest import run_ingestion
from loguru import logger

router = APIRouter()

@router.post("/")
async def ingest_documents(directory: str, background_tasks: BackgroundTasks, username: str = Depends(verify_token)):
    """
    Triggers document ingestion from a directory. Requires JWT auth.
    """
    logger.info(f"User {username} triggered ingestion for directory: {directory}")
    
    # Run in background to avoid blocking
    background_tasks.add_task(run_ingestion, directory)
    
    return {"status": "Ingestion started in the background", "directory": directory}
