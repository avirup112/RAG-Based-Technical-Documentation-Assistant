from fastapi import APIRouter
from app.vectordb.chroma_client import get_collection

router = APIRouter()

@router.get("/")
async def list_documents():
    """
    Lists all indexed documents.
    """
    collection = get_collection()
    
    # In a real app, you should paginate this.
    results = collection.get(limit=100, include=['metadatas'])
    
    docs = []
    if results['metadatas']:
        for meta in results['metadatas']:
            source = meta.get('source')
            if source and source not in docs:
                docs.append(source)
                
    # Deduplicate sources
    unique_sources = list(set(docs))
    
    return {
        "total_chunks": len(results['ids']),
        "unique_documents": len(unique_sources),
        "documents": unique_sources
    }
