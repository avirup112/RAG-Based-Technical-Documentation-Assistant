from langchain.text_splitter import RecursiveCharacterTextSplitter
from app.core.config import settings
from typing import List, Dict


def chunk_documents(documents: List[Dict[str, str]]) -> List[Dict[str, str]]:
    """
    Splits documents into chunks.
    """
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=settings.CHUNK_SIZE,
        chunk_overlap=settings.CHUNK_OVERLAP,
        separators=["\\n\\n", "\\n", " ", ""],
    )

    chunks = []
    for doc in documents:
        texts = splitter.split_text(doc["content"])
        for i, text in enumerate(texts):
            chunks.append({"content": text, "source": doc["source"], "chunk_index": i})
    return chunks
