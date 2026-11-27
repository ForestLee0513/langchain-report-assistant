from sqlalchemy import text
import torch
from openai import OpenAIError

from app.core.db import get_db
from app.core.logger import get_logger
from app.core.settings import settings
from app.core.llm import get_llm


logger = get_logger(__name__)


def db_preflight() -> bool:
    """DB 접속 가능 여부를 확인합니다.
    
    Return: Boolean"""
    
    try:
        with get_db().connect() as transaction:
            transaction.execute(text("SELECT 1"))

        return True
    except:
        logger.exception("DB is not initialized.")
        return False


def gpu_preflight() -> dict | None:
    """GPU 가속가능 여부를 확인합니다.
    
    Apple MPS도 지원 범위에 포함합니다.
    
    Return: 선택된 GPU의 하드웨어 정보 | None"""

    try:
        # CUDA
        if torch.cuda.is_available():
            idx = torch.cuda.current_device()
            return {
                "type": "cuda",
                "device": f"cuda:{idx}",
                "name": torch.cuda.get_device_name(idx),
                "count": torch.cuda.device_count(),
            }

        # Apple MPS
        if torch.backends.mps.is_available():
            return {
                "type": "mps",
                "device": torch.device("mps"),
                "name": "Apple Silicon GPU (MPS)",
                "count": 1,
            }
    except:
        logger.exception("GPU acceleration failed")
    return None


def llm_preflight() -> bool:
    """OpenAI API 접근 가능 여부(키 유효성 + 네트워크)를 확인합니다.

    토큰을 소모하지 않는 모델 조회 API를 사용합니다.

    Return: bool
    """
    if not settings.OPENAI_API_KEY:
        logger.error("llm preflight failed: OPENAI_API_KEY is empty")
        return False

    try:
        client = get_llm()
        # 헬스체크용: 재시도 없이, 짧은 타임아웃
        client.with_options(timeout=5.0, max_retries=0).models.retrieve(
            settings.LLM_MODEL
        )
        return True
    except OpenAIError:
        logger.exception("LLM preflight failed")
        return False
    except Exception:
        logger.exception("LLM preflight unexpected error")
        return False