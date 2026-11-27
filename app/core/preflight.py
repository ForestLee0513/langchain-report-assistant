from sqlalchemy import text
import torch

from app.core.db import db
from app.core.logger import get_logger


logger = get_logger(__name__)


def db_preflight() -> bool:
    """DB 접속 가능 여부를 확인합니다.
    
    Return: Boolean"""
    
    try:
        with db.connect() as transaction:
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
