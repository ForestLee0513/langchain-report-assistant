import os


class Settings():
    PROJECT_NAME = "Langchain report assistant"
    API_V1_STR = "/api/v1"

    # Database
    DATABASE_URL = os.getenv("DATABASE_URL")

    # LLM
    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY") 
    LLM_MODEL = os.getenv("LLM_MODEL") 

    # Embedding
    EMBEDDING_MODEL = os.getenv("EMBEDDING_MODEL") 
    RERANKER_MODEL = os.getenv("RERANKER_MODEL") 
    RETRIEVE_K = os.getenv("RETRIEVE_K", 8)
    CONTEXT_K = os.getenv("CONTEXT_K", 3)

    # Agent
    MAX_TOOL_CALLS = os.getenv("MAX_TOOL_CALLS", 4)
    MAX_MODEL_CALLS = os.getenv("MAX_MODEL_CALLS", 14)
    LLM_TIMEOUT_SECONDS = os.getenv("LLM_TIMEOUT_SECONDS", 30)
    CONTEXT_CHARS = os.getenv("CONTEXT_CHARS", 9000)
    RERANK_BATCH_SIZE = os.getenv("RERANK_BATCH_SIZE", 2)
    RERANK_MAX_LENGTH = os.getenv("RERANK_MAX_LENGTH", 512)
    DB_TIMEOUT_MS = os.getenv("DB_TIMEOUT_MS", 10000)

    # Langsmith
    LANGSMITH_TRACING = os.getenv("LANGSMITH_TRACING", False)
    LANGCHAIN_TRACING_V2 = os.getenv("LANGCHAIN_TRACING_V2", False)

    # Validation example params
    DAY30_REPORT_ID = os.getenv("DAY30_REPORT_ID", 63)
    DAY30_MISSING_ID = os.getenv("DAY30_MISSING_ID", 999999)

    # Logger
    LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO").upper()
    LOG_DIR: str = os.getenv("LOG_DIR", "logs")
    LOG_TO_FILE: bool = os.getenv("LOG_TO_FILE", "false").lower() in {"1", "true", "yes", "on"}


settings = Settings()