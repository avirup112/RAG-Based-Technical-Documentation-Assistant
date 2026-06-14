from app.graph.state import GraphState
from app.core.llm import get_judge_llm
from app.auth.agent_auth import sign_payload
from app.core.constants import SENDER_GRADER
from loguru import logger
from langsmith import traceable

@traceable
def grading_node(state: GraphState) -> GraphState:
    """
    Evaluates relevance and performs Contextual Compression.
    Instead of just returning yes/no, it extracts ONLY the parts of the 
    document that are relevant to the user's question, discarding the fluff.
    """
    question = state.get("rewritten_question", state["question"])
    docs = state.get("reranked_docs", [])
    
    if not docs:
        return state
        
    llm = get_judge_llm(temperature=0.0)
    relevant_docs = []
    
    logger.info(f"Contextual Compression: Processing {len(docs)} documents...")
    
    for doc in docs:
        prompt = f"""
        You are a strict contextual compressor for a retrieval system.
        Your job is to read the following document and extract ONLY the sentences, paragraphs, or code snippets that are directly relevant to answering the user's question.
        
        Rules:
        1. If the document contains NO relevant information to the question, you MUST reply with exactly one word: IRRELEVANT.
        2. If the document IS relevant, return ONLY the exact relevant text extracted from the document. Do not add conversational filler.
        3. Do not summarize; extract the original text as closely as possible.
        
        User Question: {question}
        
        Document Content:
        {doc['content']}
        
        Extraction:
        """
        response = llm.invoke(prompt)
        compressed_text = response.content.strip()
        
        # If the LLM didn't flag it as irrelevant, we keep it and replace the content with the compressed version
        if compressed_text.upper() != "IRRELEVANT" and "IRRELEVANT" not in compressed_text[:20].upper():
            # Create a copy so we don't mutate the original state directly
            compressed_doc = doc.copy()
            
            # Log the compression ratio for debugging
            original_len = len(doc['content'])
            new_len = len(compressed_text)
            logger.debug(f"Compressed chunk from {original_len} to {new_len} chars ({(new_len/original_len)*100:.1f}%)")
            
            # Replace the chunky original text with the lean compressed text
            compressed_doc['content'] = compressed_text
            relevant_docs.append(compressed_doc)
            
    logger.info(f"Contextual Compression complete. Kept {len(relevant_docs)} highly relevant snippets.")
            
    return {
        **state,
        "relevant_docs": relevant_docs,
        "sender_metadata": {
            "sender": SENDER_GRADER,
            "signature": sign_payload(SENDER_GRADER, {"relevant_count": len(relevant_docs)})
        }
    }
