from functools import lru_cache

from openai import OpenAI

from app.core.logger import get_logger
from app.core.settings import settings


logger = get_logger(__name__)


@lru_cache(maxsize=1)
def get_llm() -> OpenAI:
    try:
        return OpenAI(
            api_key=settings.OPENAI_API_KEY,
            timeout=settings.LLM_TIMEOUT_SECONDS
        )
    except Exception:
        logger.exception("failed to create openai client")
        raise