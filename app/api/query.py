from fastapi import APIRouter, Depends
from app.models.schemas import QueryRequest, QueryResponse
from app.auth.jwt_auth import verify_token
from app.graph.workflow import build_workflow
from app.utils.citations import extract_citations
from loguru import logger

router = APIRouter()
graph = build_workflow()

@router.post("/", response_model=QueryResponse)
async def query_assistant(request: QueryRequest, username: str = Depends(verify_token)):
    """
    Query the RAG assistant. Requires JWT auth.
    """
    logger.info(f"User {username} asked: {request.question} in session: {request.session_id}")
    
    initial_state = {
        "question": request.question,
        "session_id": request.session_id
    }
    
    # Run the graph
    try:
        final_state = graph.invoke(initial_state)
    except Exception as e:
        logger.error(f"Error executing graph: {e}")
        return QueryResponse(
            answer="An error occurred while processing your query.",
            sources=[],
            hallucination_score="fail"
        )
    
    answer = final_state.get("answer", "No answer generated.")
    relevant_docs = final_state.get("relevant_docs", [])
    hallucination_score = final_state.get("hallucination_score", "unknown")
    
    sources = extract_citations(relevant_docs)
    
    logger.info(f"Query completed. Hallucination score: {hallucination_score}")
    
    return QueryResponse(
        answer=answer,
        sources=sources,
        hallucination_score=hallucination_score
    )
