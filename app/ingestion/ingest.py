from app.ingestion.loader import load_markdown_files
from app.ingestion.chunker import chunk_documents
from app.ingestion.metadata import extract_metadata
from app.ingestion.embedder import prepare_for_embedding
from app.vectordb.chroma_client import get_collection
from loguru import logger


def run_ingestion(directory: str):
    """
    Runs the full ingestion pipeline: Load -> Chunk -> Metadata -> Embed -> Store
    """
    logger.info(f"Starting ingestion from {directory}")

    # 1. Load
    docs = load_markdown_files(directory)
    logger.info(f"Loaded {len(docs)} files")
    if not docs:
        return

    # 2. Chunk
    chunks = chunk_documents(docs)
    logger.info(f"Created {len(chunks)} chunks")

    # 3. Metadata
    logger.info("Extracting metadata for chunks...")
    for chunk in chunks:
        meta = extract_metadata(chunk["content"], chunk["source"])
        chunk["metadata"] = {
            "source": chunk["source"],
            "framework": meta.get("framework", "unknown"),
            "section": meta.get("section", "unknown"),
            "doc_type": meta.get("doc_type", "unknown"),
        }

    # 4. Embed
    logger.info("Generating embeddings...")
    chunks = prepare_for_embedding(chunks)

    # 5. Store in Chroma
    logger.info("Storing in ChromaDB...")
    collection = get_collection()

    ids = [c["chunk_id"] for c in chunks]
    embeddings = [c["embedding"] for c in chunks]
    documents = [c["content"] for c in chunks]

    # Chroma requires metadata values to be str, int, float or bool
    metadatas = []
    for c in chunks:
        m = c["metadata"].copy()
        m["chunk_id"] = c["chunk_id"]
        metadatas.append(m)

    # Batch add to ChromaDB to avoid "exceeds maximum batch size" error
    batch_size = 100
    for i in range(0, len(ids), batch_size):
        collection.add(
            ids=ids[i : i + batch_size],
            embeddings=embeddings[i : i + batch_size],
            documents=documents[i : i + batch_size],
            metadatas=metadatas[i : i + batch_size],
        )

    logger.info(f"Successfully ingested {len(chunks)} chunks.")
