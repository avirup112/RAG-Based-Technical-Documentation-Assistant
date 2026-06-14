from typing import Dict, Any

def create_chroma_filter(metadata: Dict[str, Any]) -> Dict[str, Any]:
    """
    Converts extracted metadata into a ChromaDB filter dictionary.
    """
    if not metadata:
        return None
        
    filters = []
    for key, value in metadata.items():
        if value and key in ["framework", "section", "doc_type"]:
            # Basic equality filter
            filters.append({key: {"$eq": value}})
            
    if not filters:
        return None
        
    if len(filters) == 1:
        return filters[0]
        
    return {"$and": filters}
