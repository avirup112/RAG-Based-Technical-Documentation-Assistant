import os
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    PROJECT_NAME: str = "RAG-Based Technical Documentation Assistant"
    API_V1_STR: str = "/api/v1"
    
    GROQ_API_KEY: str = ""
    JWT_SECRET_KEY: str = "super_secret_jwt_key_please_change_in_production"
    AGENT_SECRET_KEY: str = "super_secret_agent_key_please_change_in_production"
    TAVILY_API_KEY: str = ""
    MONGODB_URI: str = "mongodb://localhost:27017/"
    
    CHROMA_DB_DIR: str = "./chroma_data"
    EMBEDDING_MODEL: str = "sentence-transformers/all-MiniLM-L6-v2"
    RERANKER_MODEL: str = "BAAI/bge-reranker-base"
    
    CHUNK_SIZE: int = 1000
    CHUNK_OVERLAP: int = 200
    
    MAX_RETRIES: int = 2
    
    LANGCHAIN_TRACING_V2: str = "false"
    LANGCHAIN_API_KEY: str = ""
    LANGCHAIN_PROJECT: str = "rag-doc-assistant"
    
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

settings = Settings()

# LangSmith SDK reads directly from os.environ, so we must push these values
# from pydantic-settings back out to the OS environment.
if settings.LANGCHAIN_TRACING_V2.lower() == "true":
    os.environ["LANGCHAIN_TRACING_V2"] = settings.LANGCHAIN_TRACING_V2
    os.environ["LANGCHAIN_API_KEY"] = settings.LANGCHAIN_API_KEY
    os.environ["LANGCHAIN_PROJECT"] = settings.LANGCHAIN_PROJECT
