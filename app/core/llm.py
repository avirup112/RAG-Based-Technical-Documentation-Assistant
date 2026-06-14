from langchain_groq import ChatGroq
from app.core.config import settings
from langchain.globals import set_llm_cache
from langchain.cache import InMemoryCache

# Enable global in-memory caching for all LLM calls
set_llm_cache(InMemoryCache())

def get_llm(temperature: float = 0.0) -> ChatGroq:
    """
    Initializes the LLaMA 3.1 8B Instant model via Groq, used as the main generator.
    Fast and efficient for retrieval-augmented generation tasks.
    """
    return ChatGroq(
        model="llama-3.1-8b-instant",
        api_key=settings.GROQ_API_KEY,
        temperature=temperature
    )

def get_judge_llm(temperature: float = 0.0) -> ChatGroq:
    """
    Initializes the LLaMA 3.3 70B Versatile model via Groq, used for LLM-as-a-Judge tasks.
    Larger model for higher-quality grading, hallucination checks, and security evaluation.
    """
    return ChatGroq(
        model="llama-3.3-70b-versatile",
        api_key=settings.GROQ_API_KEY,
        temperature=temperature
    )
