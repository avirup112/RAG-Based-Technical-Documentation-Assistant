from langgraph.graph import StateGraph, END
from app.graph.state import GraphState
from app.core.config import settings

from app.graph.nodes.security_check import security_node
from app.graph.nodes.query_analysis import query_analysis_node
from app.graph.nodes.metadata_router import metadata_router_node
from app.graph.nodes.retrieval import retrieval_node
from app.graph.nodes.reranker import reranker_node
from app.graph.nodes.grading import grading_node
from app.graph.nodes.rewrite import rewrite_node
from app.graph.nodes.generation import generation_node
from app.graph.nodes.hallucination import hallucination_node
from app.graph.nodes.memory_loader import memory_loader_node
from app.graph.nodes.memory_saver import memory_saver_node
from app.graph.nodes.web_search import web_search_node

def decide_to_generate(state: GraphState):
    """
    Conditional edge logic: Decide whether to generate an answer, rewrite, or use web search.
    """
    relevant_docs = state.get("relevant_docs", [])
    retries = state.get("retries", 0)
    
    if len(relevant_docs) > 0:
        return "generate"
    elif retries >= settings.MAX_RETRIES:
        return "web_search"
    else:
        return "rewrite"

def build_workflow() -> StateGraph:
    """
    Builds the Self-Corrective RAG LangGraph workflow.
    """
    workflow = StateGraph(GraphState)
    
    # Add nodes
    workflow.add_node("memory_loader", memory_loader_node)
    workflow.add_node("security", security_node)
    workflow.add_node("analyze", query_analysis_node)
    workflow.add_node("route", metadata_router_node)
    workflow.add_node("retrieve", retrieval_node)
    workflow.add_node("rerank", reranker_node)
    workflow.add_node("grade", grading_node)
    workflow.add_node("rewrite", rewrite_node)
    workflow.add_node("web_search", web_search_node)
    workflow.add_node("generate", generation_node)
    workflow.add_node("hallucination", hallucination_node)
    workflow.add_node("memory_saver", memory_saver_node)
    
    # Define edges
    workflow.set_entry_point("memory_loader")
    workflow.add_edge("memory_loader", "security")
    
    # Security blocks execution if failed
    def check_security(state: GraphState):
        if state.get("error"):
            return "end"
        return "continue"
        
    workflow.add_conditional_edges(
        "security",
        check_security,
        {"end": END, "continue": "analyze"}
    )
    
    workflow.add_edge("analyze", "route")
    workflow.add_edge("route", "retrieve")
    workflow.add_edge("retrieve", "rerank")
    workflow.add_edge("rerank", "grade")
    
    workflow.add_conditional_edges(
        "grade",
        decide_to_generate,
        {
            "generate": "generate",
            "rewrite": "rewrite",
            "web_search": "web_search"
        }
    )
    
    workflow.add_edge("rewrite", "analyze") # Loop back through full transformation pipeline
    workflow.add_edge("web_search", "generate")
    workflow.add_edge("generate", "hallucination")
    workflow.add_edge("hallucination", "memory_saver")
    workflow.add_edge("memory_saver", END)
    
    return workflow.compile()
