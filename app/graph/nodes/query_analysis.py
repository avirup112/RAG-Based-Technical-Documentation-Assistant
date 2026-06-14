import re
import json
from typing import List
from app.graph.state import GraphState
from app.security.pii_detector import redact_pii
from app.core.llm import get_llm
from loguru import logger
from langsmith import traceable


# ─────────────────────────────────────────────
# Stage 1: Query Decomposition
# ─────────────────────────────────────────────
@traceable
def decompose_query(question: str) -> List[str]:
    """
    Breaks a complex question into focused sub-questions using an LLM.
    If the question is simple enough, it returns it as-is.
    """
    llm = get_llm(temperature=0.0)
    prompt = f"""
    You are an expert at breaking complex technical questions into simpler sub-questions.
    
    Given the following user question, decompose it into a list of 1 to 3 focused sub-questions
    that together cover the full intent. If the question is already simple and focused, return
    it as a single-item list.
    
    Return ONLY a valid JSON array of strings. No explanation, no markdown.
    
    Question: {question}
    
    Example output: ["What is X?", "How do I configure Y?"]
    """
    try:
        response = llm.invoke(prompt)
        text = response.content.strip()
        # Strip markdown code fences if present
        text = re.sub(r"^```json\s*|^```\s*|```$", "", text, flags=re.MULTILINE).strip()
        sub_questions = json.loads(text)
        if not isinstance(sub_questions, list) or len(sub_questions) == 0:
            return [question]
        logger.info(f"Decomposed into {len(sub_questions)} sub-questions: {sub_questions}")
        return sub_questions
    except Exception as e:
        logger.error(f"Query decomposition failed: {e}")
        return [question]


# ─────────────────────────────────────────────
# Stage 2: Query Expansion
# ─────────────────────────────────────────────
@traceable
def expand_queries(sub_questions: List[str]) -> List[str]:
    """
    For each sub-question, generates alternative phrasings and keyword expansions.
    Returns a flat deduplicated list of all search queries.
    """
    llm = get_llm(temperature=0.2)
    all_queries = list(sub_questions)  # always include originals

    for question in sub_questions:
        prompt = f"""
        You are a search query expert. Given a technical question, generate 2 alternative
        phrasings or keyword-expanded variations that would help retrieve relevant documentation.
        Focus on synonyms, related concepts, and alternative technical terminology.
        
        Return ONLY a valid JSON array of 2 strings. No explanation, no markdown.
        
        Question: {question}
        
        Example output: ["alternative phrasing 1", "alternative phrasing 2"]
        """
        try:
            response = llm.invoke(prompt)
            text = response.content.strip()
            text = re.sub(r"^```json\s*|^```\s*|```$", "", text, flags=re.MULTILINE).strip()
            variants = json.loads(text)
            if isinstance(variants, list):
                all_queries.extend(variants)
        except Exception as e:
            logger.error(f"Query expansion failed for '{question}': {e}")

    # Deduplicate while preserving order
    seen = set()
    unique_queries = []
    for q in all_queries:
        if q not in seen:
            seen.add(q)
            unique_queries.append(q)

    logger.info(f"Expanded to {len(unique_queries)} total search queries.")
    return unique_queries


# ─────────────────────────────────────────────
# Stage 3: Query Type Classification
# ─────────────────────────────────────────────
@traceable
def classify_query(question: str) -> str:
    """
    Classifies the question type to guide downstream processing.
    Returns: 'how_to', 'conceptual', 'api_reference', or 'troubleshooting'
    """
    llm = get_llm(temperature=0.0)
    prompt = f"""
    Classify the following technical question into exactly one of these types:
    - how_to: Step-by-step instructions (e.g. "How do I install X?")
    - conceptual: Explanation of ideas or architecture (e.g. "What is dependency injection?")
    - api_reference: Questions about specific classes, methods, or parameters (e.g. "What does @router.get() do?")
    - troubleshooting: Error debugging or problem solving (e.g. "Why is X failing?")
    
    Return ONLY the type label, nothing else.
    
    Question: {question}
    """
    try:
        response = llm.invoke(prompt)
        label = response.content.strip().lower()
        if label not in ("how_to", "conceptual", "api_reference", "troubleshooting"):
            return "conceptual"  # safe default
        logger.info(f"Query classified as: {label}")
        return label
    except Exception as e:
        logger.error(f"Query classification failed: {e}")
        return "conceptual"


# ─────────────────────────────────────────────
# Main Node
# ─────────────────────────────────────────────
@traceable
def query_analysis_node(state: GraphState) -> GraphState:
    """
    Full Query Transformation Pipeline:
      1. PII Redaction (Microsoft Presidio)
      2. Query Decomposition  → breaks complex questions into sub-questions
      3. Query Expansion      → adds synonyms and alternative phrasings for each sub-question
      4. Query Classification → identifies query type to guide downstream routing
    """
    # Use rewritten question from a retry cycle if available, otherwise use original
    raw_question = state.get("rewritten_question") or state["question"]

    # Stage 0: Redact PII
    safe_question = redact_pii(raw_question)
    cleaned_question = re.sub(r'\s+', ' ', safe_question).strip()
    logger.info(f"Query Analysis started. Cleaned question: {cleaned_question}")

    # Stage 1: Decompose
    sub_questions = decompose_query(cleaned_question)

    # Stage 2: Expand each sub-question
    expanded_queries = expand_queries(sub_questions)

    # Stage 3: Classify the original (cleaned) question
    query_type = classify_query(cleaned_question)

    return {
        **state,
        "question": state["question"],           # always preserve original raw question
        "rewritten_question": cleaned_question,  # cleaned version for downstream
        "sub_questions": sub_questions,
        "expanded_queries": expanded_queries,
        "query_type": query_type,
    }
