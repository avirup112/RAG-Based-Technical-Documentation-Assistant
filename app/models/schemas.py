from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
import uuid


class QueryRequest(BaseModel):
    session_id: str = Field(
        default_factory=lambda: str(uuid.uuid4()),
        description="The session ID for conversation memory",
    )
    question: str = Field(
        ..., description="The technical question to ask the assistant"
    )


class Citation(BaseModel):
    source: str
    chunk_id: str
    content_snippet: str


class QueryResponse(BaseModel):
    answer: str
    sources: List[Citation]
    hallucination_score: str


class FeedbackRequest(BaseModel):
    session_id: Optional[str] = None
    question: str
    answer: str
    is_helpful: bool
    comments: Optional[str] = None


class DocumentMetadata(BaseModel):
    source: str
    framework: str
    section: str
    doc_type: str
    chunk_id: str


class Token(BaseModel):
    access_token: str
    token_type: str


class AgentMessage(BaseModel):
    sender: str
    signature: str
    payload: Dict[str, Any]
